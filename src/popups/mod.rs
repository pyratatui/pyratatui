// src/popups/mod.rs
//! Python bindings for `tui-popup` — centered popup overlay widget.
//!
//! tui-popup API (confirmed from docs.rs/tui-popup):
//!
//! ```rust
//! // Stateless (simple string body):
//! let popup = Popup::new("Press any key to exit")
//!     .title("tui-popup demo")
//!     .style(Style::new().white().on_blue());
//! frame.render_widget(popup, frame.area());
//!
//! // Stateful (draggable):
//! frame.render_stateful_widget(popup, frame.area(), popup_state);
//!
//! // Scrollable body via KnownSizeWrapper:
//! let sized = KnownSizeWrapper { inner: paragraph, width: 21, height: 5 };
//! let popup = Popup::new(sized).title("scroll").style(...);
//! frame.render_widget(popup, frame.area());
//! ```
//!
//! `PopupState` movement:
//! - `state.move_up(n)` / `move_down(n)` / `move_left(n)` / `move_right(n)`
//! - `state.mouse_down(col, row)` / `mouse_up(col, row)` / `mouse_drag(col, row)`

use pyo3::prelude::*;
use ratatui::{
    layout::Rect as RRect,
    style::Style as RStyle,
    text::{Line as RLine, Text as RText},
    widgets::{Paragraph as RParagraph, Wrap},
    Frame as RFrame,
};
use tui_popup::{
    KnownSizeWrapper as TKnownSizeWrapper, Popup as TPopup, PopupState as TPopupState,
};

use crate::style::Style;

// ── KnownSizeWrapper ─────────────────────────────────────────────────────────

/// Wraps a scrollable text body with explicit dimensions for use inside a `Popup`.
///
/// ```python
/// from pyratatui import KnownSizeWrapper, Popup
///
/// lines = [f"Line {i}" for i in range(30)]
/// body  = KnownSizeWrapper(lines, width=40, height=10)
/// popup = Popup(body).title("Scrollable popup")
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct KnownSizeWrapper {
    pub(crate) lines: Vec<String>,
    pub(crate) width: u16,
    pub(crate) height: u16,
    pub(crate) scroll: u16,
}

#[pymethods]
impl KnownSizeWrapper {
    #[new]
    #[pyo3(signature = (lines, width, height, scroll=0))]
    pub fn new(lines: Vec<String>, width: u16, height: u16, scroll: u16) -> Self {
        Self {
            lines,
            width,
            height,
            scroll,
        }
    }

    pub fn with_scroll(&self, scroll: u16) -> Self {
        Self {
            scroll,
            ..self.clone()
        }
    }

    #[getter]
    pub fn scroll(&self) -> u16 {
        self.scroll
    }

    pub fn scroll_down(&mut self, n: u16) {
        let max = (self.lines.len() as u16).saturating_sub(self.height);
        self.scroll = (self.scroll + n).min(max);
    }
    pub fn scroll_up(&mut self, n: u16) {
        self.scroll = self.scroll.saturating_sub(n);
    }

    fn __repr__(&self) -> String {
        format!(
            "KnownSizeWrapper(lines={}, {}×{}, scroll={})",
            self.lines.len(),
            self.width,
            self.height,
            self.scroll
        )
    }
}

impl KnownSizeWrapper {
    /// Build the `tui_popup::KnownSizeWrapper<Paragraph>` expected by tui-popup.
    pub(crate) fn to_tui(&self) -> TKnownSizeWrapper<RParagraph<'static>> {
        let text = RText::from(
            self.lines
                .iter()
                .map(|l| RLine::raw(l.clone()))
                .collect::<Vec<_>>(),
        );
        let inner = RParagraph::new(text)
            .wrap(Wrap { trim: false })
            .scroll((self.scroll, 0));
        TKnownSizeWrapper {
            inner,
            width: self.width as usize,
            height: self.height as usize,
        }
    }
}

// ── PopupState ────────────────────────────────────────────────────────────────

/// State for a draggable / moveable `Popup`.
///
/// ```python
/// from pyratatui import Popup, PopupState
///
/// state = PopupState()
///
/// def ui(frame):
///     popup = Popup("Hello!").title("Demo")
///     frame.render_stateful_popup(popup, frame.area, state)
///
/// # Move with arrow keys:
/// state.move_up(1)
/// state.move_down(1)
/// ```
#[pyclass(module = "pyratatui", unsendable)]
#[derive(Debug)]
pub struct PopupState {
    pub(crate) inner: TPopupState,
}

#[pymethods]
impl PopupState {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: TPopupState::default(),
        }
    }

    pub fn move_up(&mut self, n: u16) {
        self.inner.move_up(n);
    }
    pub fn move_down(&mut self, n: u16) {
        self.inner.move_down(n);
    }
    pub fn move_left(&mut self, n: u16) {
        self.inner.move_left(n);
    }
    pub fn move_right(&mut self, n: u16) {
        self.inner.move_right(n);
    }

    pub fn mouse_down(&mut self, col: u16, row: u16) {
        self.inner.mouse_down(col, row);
    }
    pub fn mouse_up(&mut self, col: u16, row: u16) {
        self.inner.mouse_up(col, row);
    }
    pub fn mouse_drag(&mut self, col: u16, row: u16) {
        self.inner.mouse_drag(col, row);
    }

    pub fn reset(&mut self) {
        self.inner = TPopupState::default();
    }

    fn __repr__(&self) -> String {
        "PopupState(<pos>)".to_string()
    }
}

// ── Popup ─────────────────────────────────────────────────────────────────────

/// A centered popup overlay widget.
///
/// ```python
/// from pyratatui import Popup, Style, Color
///
/// # Simple string popup (stateless):
/// popup = (
///     Popup("Press any key to exit")
///     .title("tui-popup demo")
///     .style(Style().fg(Color.white()).bg(Color.blue()))
/// )
/// frame.render_popup(popup, frame.area)
///
/// # Scrollable popup (stateless):
/// body = KnownSizeWrapper(lines, 40, 10)
/// popup = Popup(body).title("Scrollable")
/// frame.render_popup(popup, frame.area)
///
/// # Draggable popup (stateful):
/// state = PopupState()
/// frame.render_stateful_popup(popup, frame.area, state)
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct Popup {
    pub(crate) body: PopupBody,
    pub(crate) title: Option<String>,
    pub(crate) style: Option<RStyle>,
}

#[derive(Clone, Debug)]
pub(crate) enum PopupBody {
    Text(String),
    Sized(KnownSizeWrapper),
}

#[pymethods]
impl Popup {
    /// Create a `Popup` from a `str` or `KnownSizeWrapper`.
    #[new]
    pub fn new(content: &Bound<'_, PyAny>) -> PyResult<Self> {
        if let Ok(text) = content.extract::<String>() {
            return Ok(Self {
                body: PopupBody::Text(text),
                title: None,
                style: None,
            });
        }
        if let Ok(wrapper) = content.extract::<PyRef<KnownSizeWrapper>>() {
            return Ok(Self {
                body: PopupBody::Sized(wrapper.clone()),
                title: None,
                style: None,
            });
        }
        Err(pyo3::exceptions::PyTypeError::new_err(
            "Popup body must be str or KnownSizeWrapper",
        ))
    }

    pub fn title(&self, title: &str) -> Self {
        Self {
            title: Some(title.to_string()),
            ..self.clone()
        }
    }
    pub fn style(&self, style: &Style) -> Self {
        Self {
            style: Some(style.inner),
            ..self.clone()
        }
    }

    fn __repr__(&self) -> String {
        let preview = match &self.body {
            PopupBody::Text(t) => format!("{:?}", t),
            PopupBody::Sized(w) => w.__repr__(),
        };
        format!("Popup(body={}, title={:?})", preview, self.title)
    }
}

// ── Render helpers ────────────────────────────────────────────────────────────

/// Render a stateless `Popup` (fixed center).
///
/// tui-popup API: `Popup::new(content).title(t).style(s)` then `render_widget(popup, area)`.
pub(crate) fn render_popup_text(frame: &mut RFrame<'_>, popup: &Popup, area: RRect) {
    match &popup.body {
        PopupBody::Text(body) => {
            let mut p = TPopup::new(body.as_str());
            if let Some(ref t) = popup.title {
                p = p.title(t.as_str());
            }
            if let Some(s) = popup.style {
                p = p.style(s);
            }
            frame.render_widget(p, area);
        }
        PopupBody::Sized(wrapper) => {
            let tui = wrapper.to_tui();
            let mut p = TPopup::new(tui);
            if let Some(ref t) = popup.title {
                p = p.title(t.as_str());
            }
            if let Some(s) = popup.style {
                p = p.style(s);
            }
            frame.render_widget(p, area);
        }
    }
}

/// Render a stateful `Popup` (draggable).
pub(crate) fn render_stateful_popup_text(
    frame: &mut RFrame<'_>,
    popup: &Popup,
    area: RRect,
    state: &mut PopupState,
) {
    match &popup.body {
        PopupBody::Text(body) => {
            let mut p = TPopup::new(body.as_str());
            if let Some(ref t) = popup.title {
                p = p.title(t.as_str());
            }
            if let Some(s) = popup.style {
                p = p.style(s);
            }
            frame.render_stateful_widget(p, area, &mut state.inner);
        }
        PopupBody::Sized(wrapper) => {
            let tui = wrapper.to_tui();
            let mut p = TPopup::new(tui);
            if let Some(ref t) = popup.title {
                p = p.title(t.as_str());
            }
            if let Some(s) = popup.style {
                p = p.style(s);
            }
            frame.render_stateful_widget(p, area, &mut state.inner);
        }
    }
}

// ── Module registration ───────────────────────────────────────────────────────

pub fn register_popups(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<KnownSizeWrapper>()?;
    m.add_class::<PopupState>()?;
    m.add_class::<Popup>()?;
    Ok(())
}
