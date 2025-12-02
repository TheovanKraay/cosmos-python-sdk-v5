use pyo3::prelude::*;
use pyo3::types::PyDict;
use azure_data_cosmos::CosmosClient as RustCosmosClient;
use std::sync::Arc;
use crate::database::DatabaseClient;
use crate::exceptions::map_error;
use once_cell::sync::Lazy;
use tokio::runtime::Runtime;

static TOKIO_RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .expect("Failed to create Tokio runtime")
});

#[pyclass(subclass)]
pub struct CosmosClient {
    inner: Arc<RustCosmosClient>,
    endpoint: String,
}

#[pymethods]
impl CosmosClient {
    #[new]
    #[pyo3(signature = (url, credential=None, **kwargs))]
    pub fn new(
        url: String,
        credential: Option<PyObject>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<Self> {
        Python::with_gil(|py| {
            let client = if let Some(cred) = credential {
                // Check if credential is a string (key-based auth)
                if let Ok(key) = cred.extract::<String>(py) {
                    RustCosmosClient::with_key(&url, key.into(), None)
                        .map_err(map_error)?
                } else {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        "Only key-based authentication is currently supported"
                    ));
                }
            } else {
                return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "credential parameter is required"
                ));
            };

            Ok(Self {
                inner: Arc::new(client),
                endpoint: url,
            })
        })
    }

    /// Create a new database
    #[pyo3(signature = (id, **kwargs))]
    pub fn create_database(
        &self,
        id: String,
        kwargs: Option<&PyDict>,
    ) -> PyResult<DatabaseClient> {
        let client = self.inner.clone();
        let id_clone = id.clone();
        
        let _result = TOKIO_RUNTIME.block_on(async move {
            client.create_database(&id_clone, None)
                .await
                .map_err(map_error)
        })?;

        // Return DatabaseClient like V4 does
        Ok(DatabaseClient::new(self.inner.clone(), id))
    }

    /// Get a database client
    pub fn get_database_client(&self, database_id: String) -> PyResult<DatabaseClient> {
        Ok(DatabaseClient::new(self.inner.clone(), database_id))
    }

    /// Delete a database
    #[pyo3(signature = (database_id, **kwargs))]
    pub fn delete_database(
        &self,
        py: Python,
        database_id: String,
        kwargs: Option<&PyDict>,
    ) -> PyResult<()> {
        let client = self.inner.database_client(&database_id);
        
        TOKIO_RUNTIME.block_on(async move {
            client.delete(None)
                .await
                .map_err(map_error)
        })?;

        Ok(())
    }

    /// List all databases
    #[pyo3(signature = (**kwargs))]
    pub fn list_databases<'py>(
        &self,
        py: Python<'py>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<Vec<&'py PyDict>> {
        let client = self.inner.clone();
        
        let databases = TOKIO_RUNTIME.block_on(async move {
            let mut result = Vec::new();
            let mut stream = client.query_databases("SELECT * FROM databases", None).map_err(map_error)?;
            
            use futures::StreamExt;
            while let Some(response) = stream.next().await {
                match response {
                    Ok(db) => result.push(db),
                    Err(e) => return Err(map_error(e)),
                }
            }
            
            Ok::<_, PyErr>(result)
        })?;

        let mut py_databases = Vec::new();
        for db in databases {
            let dict = PyDict::new(py);
            dict.set_item("id", format!("{:?}", db))?;
            py_databases.push(dict);
        }

        Ok(py_databases)
    }

    /// Context manager support
    pub fn __enter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    #[pyo3(signature = (exc_type=None, exc_val=None, exc_tb=None))]
    pub fn __exit__(
        &self,
        exc_type: Option<PyObject>,
        exc_val: Option<PyObject>,
        exc_tb: Option<PyObject>,
    ) -> PyResult<bool> {
        Ok(false)
    }
}
