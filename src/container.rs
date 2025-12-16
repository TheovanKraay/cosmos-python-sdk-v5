use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use azure_data_cosmos::CosmosClient as RustCosmosClient;
use azure_data_cosmos::PartitionKey as RustPartitionKey;
use std::sync::Arc;
use serde_json::Value;
use crate::exceptions::map_error;
use crate::utils::py_object_to_json;
use once_cell::sync::Lazy;
use tokio::runtime::Runtime;

// Global Tokio runtime - reused across all operations for better performance
static TOKIO_RUNTIME: Lazy<Runtime> = Lazy::new(|| {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .build()
        .expect("Failed to create Tokio runtime")
});

#[pyclass(subclass)]
pub struct ContainerClient {
    cosmos_client: Arc<RustCosmosClient>,
    database_id: String,
    container_id: String,
}

impl ContainerClient {
    pub fn new(cosmos_client: Arc<RustCosmosClient>, database_id: String, container_id: String) -> Self {
        Self {
            cosmos_client,
            database_id,
            container_id,
        }
    }
}

#[pymethods]
impl ContainerClient {
    /// Create a new item
    /// Accepts either a dict or a JSON string for the body
    #[pyo3(signature = (body, **kwargs))]
    pub fn create_item<'py>(
        &self,
        py: Python<'py>,
        body: &'py PyAny,
        kwargs: Option<&PyDict>,
    ) -> PyResult<&'py PyDict> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        // Convert Python object (dict or string) to JSON using hybrid approach
        let item_value = py_object_to_json(py, body)?;
        
        // Extract partition key from body or kwargs
        let partition_key = if let Ok(dict) = body.downcast::<PyDict>() {
            self.extract_partition_key(py, dict, kwargs)?
        } else {
            // If body is a string, partition key must come from kwargs
            self.extract_partition_key_from_kwargs(kwargs)?
        };
        
        let _result = TOKIO_RUNTIME.block_on(async move {
            container.create_item(partition_key, item_value, None)
                .await
                .map_err(map_error)
        })?;

        // Return the created item as dict (convert if it was a string)
        if let Ok(dict) = body.downcast::<PyDict>() {
            Ok(dict)
        } else {
            // If input was a string, we need to convert it back to dict for return
            let json_module = py.import("json")?;
            json_module.call_method1("loads", (body,))?.extract()
        }
    }

    /// Read an item by ID and partition key
    #[pyo3(signature = (item, partition_key, **kwargs))]
    pub fn read_item<'py>(
        &self,
        py: Python<'py>,
        item: String,
        partition_key: PyObject,
        kwargs: Option<&PyDict>,
    ) -> PyResult<&'py PyDict> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        let pk = self.python_to_partition_key(py, partition_key)?;
        let item_id = item.clone();
        
        let result = TOKIO_RUNTIME.block_on(async move {
            container.read_item::<Value>(pk, &item_id, None)
                .await
                .map_err(map_error)
        })?;

        // Extract the value from the Response
        let value = result.into_body().json::<Value>()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Failed to deserialize response: {}", e)))?;
        
        let json_str = serde_json::to_string(&value)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON error: {}", e)))?;;
        
        let json_module = py.import("json")?;
        let py_dict = json_module.call_method1("loads", (json_str,))?;
        py_dict.extract()
    }

    /// Upsert an item (create or replace)
    /// Accepts either a dict or a JSON string for the body
    #[pyo3(signature = (body, **kwargs))]
    pub fn upsert_item<'py>(
        &self,
        py: Python<'py>,
        body: &'py PyAny,
        kwargs: Option<&PyDict>,
    ) -> PyResult<&'py PyDict> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        // Convert Python object (dict or string) to JSON using hybrid approach
        let item_value = py_object_to_json(py, body)?;
        
        // Extract partition key from body or kwargs
        let partition_key = if let Ok(dict) = body.downcast::<PyDict>() {
            self.extract_partition_key(py, dict, kwargs)?
        } else {
            self.extract_partition_key_from_kwargs(kwargs)?
        };
        
        let _result = TOKIO_RUNTIME.block_on(async move {
            container.upsert_item(partition_key, item_value, None)
                .await
                .map_err(map_error)
        })?;

        // Return the created item as dict (convert if it was a string)
        if let Ok(dict) = body.downcast::<PyDict>() {
            Ok(dict)
        } else {
            let json_module = py.import("json")?;
            json_module.call_method1("loads", (body,))?.extract()
        }
    }

    /// Replace an item
    /// Accepts either a dict or a JSON string for the body
    #[pyo3(signature = (item, body, **kwargs))]
    pub fn replace_item<'py>(
        &self,
        py: Python<'py>,
        item: String,
        body: &'py PyAny,
        kwargs: Option<&PyDict>,
    ) -> PyResult<&'py PyDict> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        // Convert Python object (dict or string) to JSON using hybrid approach
        let item_value = py_object_to_json(py, body)?;
        
        // Extract partition key from body or kwargs
        let partition_key = if let Ok(dict) = body.downcast::<PyDict>() {
            self.extract_partition_key(py, dict, kwargs)?
        } else {
            self.extract_partition_key_from_kwargs(kwargs)?
        };
        let item_id = item.clone();
        
        let _result = TOKIO_RUNTIME.block_on(async move {
            container.replace_item(partition_key, &item_id, item_value, None)
                .await
                .map_err(map_error)
        })?;

        // Return the created item as dict (convert if it was a string)
        if let Ok(dict) = body.downcast::<PyDict>() {
            Ok(dict)
        } else {
            let json_module = py.import("json")?;
            json_module.call_method1("loads", (body,))?.extract()
        }
    }

    /// Delete an item
    #[pyo3(signature = (item, partition_key, **kwargs))]
    pub fn delete_item(
        &self,
        py: Python,
        item: String,
        partition_key: PyObject,
        kwargs: Option<&PyDict>,
    ) -> PyResult<()> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        let pk = self.python_to_partition_key(py, partition_key)?;
        let item_id = item.clone();
        
        TOKIO_RUNTIME.block_on(async move {
            container.delete_item(pk, &item_id, None)
                .await
                .map_err(map_error)
        })?;

        Ok(())
    }

    /// Query items with SQL
    #[pyo3(signature = (query, **kwargs))]
    pub fn query_items<'py>(
        &self,
        py: Python<'py>,
        query: String,
        kwargs: Option<&PyDict>,
    ) -> PyResult<Vec<&'py PyDict>> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        // Extract partition_key from kwargs if provided
        let partition_key_opt = if let Some(kw) = kwargs {
            if let Ok(Some(pk)) = kw.get_item("partition_key") {
                Some(self.python_to_partition_key(py, pk.into())?)
            } else {
                None
            }
        } else {
            None
        };
        
        let items = TOKIO_RUNTIME.block_on(async move {
            let mut result = Vec::new();
            
            // If no partition key is provided, we need to do a cross-partition query
            // For now, if partition_key is not specified, return error asking for it
            let pk = partition_key_opt.ok_or_else(|| {
                PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    "partition_key is required for queries. For cross-partition queries, this will be supported in a future update."
                )
            })?;
            
            let mut stream = container.query_items::<Value>(&query, pk, None).map_err(map_error)?;
            
            use futures::StreamExt;
            while let Some(response) = stream.next().await {
                match response {
                    Ok(item) => {
                        result.push(item);
                    },
                    Err(e) => return Err(map_error(e)),
                }
            }
            
            Ok::<_, PyErr>(result)
        })?;

        let mut py_items = Vec::new();
        for item in items {
            let json_str = serde_json::to_string(&item)
                .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON error: {}", e)))?;
            
            let json_module = py.import("json")?;
            let py_dict = json_module.call_method1("loads", (json_str,))?;
            py_items.push(py_dict.extract()?);
        }

        Ok(py_items)
    }

    /// Patch an item
    #[pyo3(signature = (item, partition_key, patch_operations, **kwargs))]
    pub fn patch_item<'py>(
        &self,
        py: Python<'py>,
        item: String,
        partition_key: PyObject,
        patch_operations: &PyList,
        kwargs: Option<&PyDict>,
    ) -> PyResult<&'py PyDict> {
        // For now, return error as patch is complex
        Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
            "patch_item is not yet implemented"
        ))
    }

    /// Read container properties
    #[pyo3(signature = (**kwargs))]
    pub fn read<'py>(
        &self,
        py: Python<'py>,
        kwargs: Option<&PyDict>,
    ) -> PyResult<&'py PyDict> {
        let dict = PyDict::new(py);
        dict.set_item("id", &self.container_id)?;
        Ok(dict)
    }

    /// Delete this container
    #[pyo3(signature = (**kwargs))]
    pub fn delete(&self, kwargs: Option<&PyDict>) -> PyResult<()> {
        let container = self.cosmos_client
            .database_client(&self.database_id)
            .container_client(&self.container_id);
        
        TOKIO_RUNTIME.block_on(async move {
            container.delete(None)
                .await
                .map_err(map_error)
        })?;

        Ok(())
    }

    #[getter]
    pub fn id(&self) -> PyResult<String> {
        Ok(self.container_id.clone())
    }
}

// Helper methods for ContainerClient
impl ContainerClient {
    fn python_to_partition_key(&self, py: Python, pk: PyObject) -> PyResult<RustPartitionKey> {
        if let Ok(s) = pk.extract::<String>(py) {
            Ok(RustPartitionKey::from(s))
        } else if let Ok(i) = pk.extract::<i64>(py) {
            Ok(RustPartitionKey::from(i))
        } else if let Ok(f) = pk.extract::<f64>(py) {
            Ok(RustPartitionKey::from(f))
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "Partition key must be string, int, or float"
            ))
        }
    }

    fn extract_partition_key(&self, py: Python, body: &PyDict, kwargs: Option<&PyDict>) -> PyResult<RustPartitionKey> {
        // Try to get partition_key from kwargs first
        if let Some(kw) = kwargs {
            if let Ok(Some(pk)) = kw.get_item("partition_key") {
                return self.python_to_partition_key(py, pk.into());
            }
        }
        
        // Otherwise, try common partition key fields from the body
        // Try common partition key field names (including "id" which is very common)
        let common_pk_fields = ["id", "category", "partitionKey", "pk", "type", "tenantId"];
        for field in &common_pk_fields {
            if let Ok(Some(value)) = body.get_item(field) {
                return self.python_to_partition_key(py, value.into());
            }
        }
        
        Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            "Partition key not found in body or kwargs"
        ))
    }
    
    fn extract_partition_key_from_kwargs(&self, kwargs: Option<&PyDict>) -> PyResult<RustPartitionKey> {
        Python::with_gil(|py| {
            if let Some(kw) = kwargs {
                if let Ok(Some(pk)) = kw.get_item("partition_key") {
                    return self.python_to_partition_key(py, pk.into());
                }
            }
            
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Partition key must be provided in kwargs when body is a JSON string"
            ))
        })
    }
}
