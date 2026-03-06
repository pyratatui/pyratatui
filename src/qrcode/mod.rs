// src/qrcode/mod.rs
//! Python bindings for `tui-qrcode` — the official ratatui QR-code widget.
//!
//! Uses `tui-qrcode 0.2.2` which targets `ratatui-core ^0.1` / `ratatui ^0.30`.
//!
//! ## Rust side
//! 1. `qrcode::QrCode::new(data)` encodes the raw data.
//! 2. `tui_qrcode::QrCodeWidget::new(qr)` builds the widget.
//! 3. `.colors(tui_qrcode::Colors::Inverted)` optionally inverts the palette.
//! 4. `frame.render_widget(widget, area)` draws it into the ratatui frame.
//!
//! ## Python side
//! ```python
//! from pyratatui import QrCodeWidget, QrColors, Terminal
//!
//! qr = QrCodeWidget("https://ratatui.rs").colors(QrColors.Inverted)
//!
//! with Terminal() as term:
//!     term.draw(lambda frame: frame.render_qrcode(qr, frame.area))
//!     term.poll_event(timeout_ms=10_000)
//! ```

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use qrcode::QrCode;
use ratatui::{layout::Rect as RRect, Frame as RFrame};
use tui_qrcode::{Colors as TColors, QrCodeWidget as TQrCodeWidget};

// ── QrColors ──────────────────────────────────────────────────────────────────

/// Color scheme for a `QrCodeWidget`.
///
/// ```python
/// from pyratatui import QrColors
///
/// QrColors.Default   # dark modules on light background (standard)
/// QrColors.Inverted  # light modules on dark background (suits dark terminals)
/// ```
#[pyclass(module = "pyratatui", eq, eq_int, from_py_object)]
#[derive(Clone, Debug, PartialEq)]
pub enum QrColors {
    /// Standard QR code — dark modules on light background.
    Default,
    /// Inverted — light modules on dark background (best for dark terminals).
    Inverted,
}

#[pymethods]
impl QrColors {
    fn __repr__(&self) -> String {
        format!("QrColors.{:?}", self)
    }
}

// ── QrCodeWidget ─────────────────────────────────────────────────────────────

/// Renders a QR code in the terminal using the official `tui-qrcode` crate.
///
/// `tui-qrcode` uses Unicode half-block characters for crisp, scannable output.
///
/// ```python
/// from pyratatui import Block, QrCodeWidget, QrColors, Terminal
///
/// qr = QrCodeWidget("https://example.com").colors(QrColors.Inverted)
///
/// with Terminal() as term:
///     def ui(frame):
///         block = Block().bordered().title(" QR Code ")
///         inner = block.inner(frame.area)
///         frame.render_widget(block, frame.area)
///         frame.render_qrcode(qr, inner)
///     term.draw(ui)
///     term.poll_event(timeout_ms=10_000)
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct QrCodeWidget {
    data: String,
    colors: QrColors,
}

#[pymethods]
impl QrCodeWidget {
    /// Create a new `QrCodeWidget` that will encode the given string.
    #[new]
    pub fn new(data: &str) -> Self {
        Self {
            data: data.to_string(),
            colors: QrColors::Default,
        }
    }

    /// Set the color scheme (builder pattern — returns a new widget).
    pub fn colors(&self, colors: &QrColors) -> Self {
        Self {
            colors: colors.clone(),
            ..self.clone()
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "QrCodeWidget(data={:?}, colors={:?})",
            self.data, self.colors
        )
    }
}

impl QrCodeWidget {
    /// Render the QR code into the ratatui frame using `tui-qrcode`.
    pub(crate) fn render_raw(&self, frame: &mut RFrame<'_>, area: RRect) -> PyResult<()> {
        // Step 1 — encode the data with the `qrcode` crate.
        let qr = QrCode::new(self.data.as_bytes())
            .map_err(|e| PyValueError::new_err(format!("QR encode error: {e}")))?;

        // Step 2 — build the tui-qrcode widget and apply the requested color scheme.
        //
        // `tui_qrcode::Colors::Inverted` is the only named variant; for the
        // standard/default palette we just omit the `.colors()` call.
        match self.colors {
            QrColors::Inverted => {
                frame.render_widget(TQrCodeWidget::new(qr).colors(TColors::Inverted), area);
            }
            QrColors::Default => {
                frame.render_widget(TQrCodeWidget::new(qr), area);
            }
        }

        Ok(())
    }
}

// ── Module registration ───────────────────────────────────────────────────────

pub fn register_qrcode(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<QrColors>()?;
    m.add_class::<QrCodeWidget>()?;
    Ok(())
}
