// src/image_widget/mod.rs — Python bindings for ratatui-image 10.x
//
// API:
//   Picker::halfblocks() -> Picker
//   Picker::from_fontsize((u16, u16)) -> Picker
//   picker.new_resize_protocol(DynamicImage) -> StatefulProtocol
//   StatefulImage::default() — stateful widget, state = StatefulProtocol
//   frame.render_stateful_widget(StatefulImage, area, &mut StatefulProtocol)

use pyo3::prelude::*;
use ratatui_image::{picker::Picker as RPicker, protocol::StatefulProtocol};

// ─── ImagePicker ─────────────────────────────────────────────────────────────

/// Detects terminal graphics capabilities and creates image protocols.
///
/// ```python
/// from pyratatui import ImagePicker
/// picker = ImagePicker.halfblocks()
/// state  = picker.load("photo.png")
/// ```
#[pyclass(module = "pyratatui")]
pub struct ImagePicker {
    inner: RPicker,
}

#[pymethods]
impl ImagePicker {
    /// Picker using unicode half-block characters (works in all terminals).
    #[staticmethod]
    pub fn halfblocks() -> Self {
        Self {
            inner: RPicker::halfblocks(),
        }
    }

    /// Picker with explicit character-cell pixel dimensions.
    #[staticmethod]
    #[allow(deprecated)]
    pub fn with_font_size(width_px: u16, height_px: u16) -> Self {
        Self {
            inner: RPicker::from_fontsize((width_px, height_px)),
        }
    }

    /// Load an image from `path` and return a render-ready `ImageState`.
    pub fn load(&mut self, path: &str) -> PyResult<ImageState> {
        let dyn_img = image::ImageReader::open(path)
            .map_err(|e| pyo3::exceptions::PyIOError::new_err(e.to_string()))?
            .decode()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;

        let protocol = self.inner.new_resize_protocol(dyn_img);
        Ok(ImageState {
            protocol,
            path: path.to_string(),
        })
    }

    fn __repr__(&self) -> String {
        "ImagePicker".to_string()
    }
}

// ─── ImageState ──────────────────────────────────────────────────────────────

/// Mutable render state for a loaded image.
#[pyclass(module = "pyratatui", unsendable)]
pub struct ImageState {
    pub(crate) protocol: StatefulProtocol,
    path: String,
}

#[pymethods]
impl ImageState {
    #[getter]
    pub fn path(&self) -> &str {
        &self.path
    }

    fn __repr__(&self) -> String {
        format!("ImageState({:?})", self.path)
    }
}

// ─── ImageWidget ─────────────────────────────────────────────────────────────

/// Resizing stateful image widget.
///
/// ```python
/// from pyratatui import ImagePicker, ImageWidget
/// picker = ImagePicker.halfblocks()
/// state  = picker.load("photo.png")
/// frame.render_stateful_image(ImageWidget(), area, state)
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone)]
pub struct ImageWidget;

#[pymethods]
impl ImageWidget {
    #[new]
    pub fn new() -> Self {
        Self
    }

    fn __repr__(&self) -> String {
        "ImageWidget".to_string()
    }
}

impl Default for ImageWidget {
    fn default() -> Self {
        Self::new()
    }
}

// ─── Registration ─────────────────────────────────────────────────────────────

pub fn register_image_widget(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ImagePicker>()?;
    m.add_class::<ImageState>()?;
    m.add_class::<ImageWidget>()?;
    Ok(())
}
