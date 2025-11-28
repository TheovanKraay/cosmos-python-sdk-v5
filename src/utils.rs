use pyo3::prelude::*;
use pyo3::types::{PyDict, PyString};
use serde_json::Value;
use std::collections::HashMap;

/// Convert Python dict to serde_json::Value
pub fn py_dict_to_json(py: Python, dict: &PyDict) -> PyResult<Value> {
    let json_module = py.import("json")?;
    let json_str = json_module.call_method1("dumps", (dict,))?.extract::<String>()?;
    serde_json::from_str(&json_str)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid JSON: {}", e)))
}

/// Convert serde_json::Value to Python dict
pub fn json_to_py_dict(py: Python, value: &Value) -> PyResult<PyObject> {
    let json_str = serde_json::to_string(value)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("JSON serialization error: {}", e)))?;
    
    let json_module = py.import("json")?;
    json_module.call_method1("loads", (json_str,))?.extract()
}

/// Convert Python kwargs to options
pub fn extract_kwargs(kwargs: Option<&PyDict>) -> HashMap<String, Value> {
    let mut options = HashMap::new();
    
    if let Some(kw) = kwargs {
        for (key, value) in kw.iter() {
            if let Ok(key_str) = key.extract::<String>() {
                // Extract common option types
                if let Ok(val) = value.extract::<String>() {
                    options.insert(key_str, Value::String(val));
                } else if let Ok(val) = value.extract::<i64>() {
                    options.insert(key_str, Value::Number(val.into()));
                } else if let Ok(val) = value.extract::<bool>() {
                    options.insert(key_str, Value::Bool(val));
                }
            }
        }
    }
    
    options
}
