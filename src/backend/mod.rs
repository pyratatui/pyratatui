// src/backend/mod.rs
//! Python bindings for ratatui backends.
//!
//! Currently exposes `CrosstermBackend` (the default backend on all platforms)
//! as a thin named type. Users rarely construct backends directly — the
//! `Terminal` type creates one automatically.

use pyo3::prelude::*;

/// The crossterm-based terminal backend.
///
/// This is selected automatically when you create a `Terminal()`.
/// You do not normally need to construct this yourself.
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone)]
pub struct CrosstermBackend;

#[pymethods]
impl CrosstermBackend {
    fn __repr__(&self) -> String {
        "CrosstermBackend()".to_string()
    }
}

pub fn register_backend(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CrosstermBackend>()?;
    Ok(())
}
