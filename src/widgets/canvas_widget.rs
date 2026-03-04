// src/widgets/canvas_widget.rs
// Canvas widget wrapping is complex due to closures; expose via the Terminal draw callback.
// This module is intentionally minimal — canvas drawing is handled via the Python draw callback
// system in terminal/mod.rs.
use pyo3::prelude::*;

pub fn register_canvas(_py: Python<'_>, _m: &Bound<'_, PyModule>) -> PyResult<()> {
    Ok(())
}
