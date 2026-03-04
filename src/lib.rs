// pyratatui/src/lib.rs
// Root module — wires all sub-modules into the Python extension module.
// Each sub-module is responsible for registering its own classes and functions.

use pyo3::prelude::*;

mod backend;
mod buffer;
mod effects;
mod errors;
mod layout;
mod style;
mod terminal;
mod text;
mod widgets;

/// The pyratatui extension module.
///
/// This is the Rust-side entry point. Python imports `pyratatui._pyratatui`
/// which is then re-exported via the Python `pyratatui` package.
#[pymodule]
fn _pyratatui(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register exception hierarchy first so all submodules can use them.
    errors::register_errors(py, m)?;

    // Register each domain submodule.
    style::register_style(py, m)?;
    text::register_text(py, m)?;
    layout::register_layout(py, m)?;
    buffer::register_buffer(py, m)?;
    widgets::register_widgets(py, m)?;
    backend::register_backend(py, m)?;
    terminal::register_terminal(py, m)?;
    effects::register_effects(py, m)?;

    // Top-level convenience re-exports.
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__ratatui_version__", "0.29")?;

    Ok(())
}
