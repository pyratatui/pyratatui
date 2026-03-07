// src/logger/mod.rs — Python bindings for tui-logger 0.18

use pyo3::prelude::*;
use ratatui::style::Style as RStyle;
use tui_logger::{
    TuiLoggerWidget as RTuiLoggerWidget, TuiWidgetEvent, TuiWidgetState as RTuiWidgetState,
};

use crate::style::Style;
use crate::widgets::Block;

// ─── Logger init functions ────────────────────────────────────────────────────

/// Initialise the tui-logger backend.
///
/// `level` must be one of: ``"error"``, ``"warn"``, ``"info"``, ``"debug"``,
/// ``"trace"``.  Raises ``ValueError`` for unknown levels.
///
/// ```python
/// from pyratatui import init_logger
/// init_logger("trace")
/// ```
#[pyfunction]
#[pyo3(signature = (level = "info"))]
pub fn init_logger(level: &str) -> PyResult<()> {
    let filter = parse_level(level)?;
    // init_logger returns Err if the logger is already set; that is fine —
    // just update the default level.
    let _ = tui_logger::init_logger(filter);
    tui_logger::set_default_level(filter);
    Ok(())
}

/// Emit a log message at the given level.
///
/// ```python
/// from pyratatui import log_message
/// log_message("info", "Hello from Python!")
/// ```
#[pyfunction]
#[pyo3(signature = (level, message))]
pub fn log_message(level: &str, message: &str) {
    match level.to_lowercase().as_str() {
        "error" => log::error!("{}", message),
        "warn" => log::warn!("{}", message),
        "debug" => log::debug!("{}", message),
        "trace" => log::trace!("{}", message),
        _ => log::info!("{}", message),
    }
}

fn parse_level(s: &str) -> PyResult<log::LevelFilter> {
    match s.to_lowercase().as_str() {
        "error" => Ok(log::LevelFilter::Error),
        "warn" => Ok(log::LevelFilter::Warn),
        "info" => Ok(log::LevelFilter::Info),
        "debug" => Ok(log::LevelFilter::Debug),
        "trace" => Ok(log::LevelFilter::Trace),
        other => Err(pyo3::exceptions::PyValueError::new_err(format!(
            "Unknown log level {:?}. Valid: error, warn, info, debug, trace",
            other
        ))),
    }
}

// ─── TuiWidgetState ───────────────────────────────────────────────────────────

/// Filter and navigation state for `TuiLoggerWidget`.
///
/// ```python
/// from pyratatui import TuiWidgetState
/// state = TuiWidgetState()
/// state.transition("Down")
/// state.transition("+")   # increase captured level
/// ```
#[pyclass(module = "pyratatui", unsendable)]
pub struct TuiWidgetState {
    pub(crate) inner: RTuiWidgetState,
}

#[pymethods]
impl TuiWidgetState {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: RTuiWidgetState::new(),
        }
    }

    /// Send a navigation or filter event.
    ///
    /// Recognised keys (case-insensitive):
    /// ``"up"``, ``"down"``, ``"left"``, ``"right"``,
    /// ``"pageup"``, ``"page_up"``, ``"prev_page"``,
    /// ``"pagedown"``, ``"page_down"``, ``"next_page"``,
    /// ``"hide"``, ``"h"``, ``"focus"``, ``"f"``,
    /// ``"toggle_target_focus"``, ``"toggle_target_hidden"``,
    /// ``"+"``, ``"-"``, ``"space"``, ``"escape"``.
    pub fn transition(&mut self, key: &str) {
        let ev = match key.to_lowercase().replace('_', "").as_str() {
            "escape" => TuiWidgetEvent::EscapeKey,
            "up" => TuiWidgetEvent::UpKey,
            "down" => TuiWidgetEvent::DownKey,
            "left" => TuiWidgetEvent::LeftKey,
            "right" => TuiWidgetEvent::RightKey,
            "pageup" | "prevpage" => TuiWidgetEvent::PrevPageKey,
            "pagedown" | "nextpage" => TuiWidgetEvent::NextPageKey,
            "hide" | "h" => TuiWidgetEvent::HideKey,
            "focus" | "f" => TuiWidgetEvent::FocusKey,
            "toggletargetfocus" => TuiWidgetEvent::FocusKey,
            "toggletargethidden" => TuiWidgetEvent::HideKey,
            "+" | "incrshown" => TuiWidgetEvent::PlusKey,
            "-" | "decrshown" => TuiWidgetEvent::MinusKey,
            "incrcaptured" => TuiWidgetEvent::PlusKey,
            "decrcaptured" => TuiWidgetEvent::MinusKey,
            "space" => TuiWidgetEvent::SpaceKey,
            _ => return,
        };
        self.inner.transition(ev);
    }

    fn __repr__(&self) -> String {
        "TuiWidgetState(<logger filter state>)".to_string()
    }
}

impl Default for TuiWidgetState {
    fn default() -> Self {
        Self::new()
    }
}

// ─── TuiLoggerWidget ─────────────────────────────────────────────────────────

/// Scrolling log-viewer widget.
///
/// ```python
/// from pyratatui import TuiLoggerWidget, TuiWidgetState, Block, Style, Color
/// logger = (
///     TuiLoggerWidget()
///         .block(Block().bordered().title(" Logs "))
///         .error_style(Style().fg(Color.red()).bold())
/// )
/// state = TuiWidgetState()
/// frame.render_logger(logger, area, state)
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone)]
pub struct TuiLoggerWidget {
    pub(crate) block: Option<Block>,
    pub(crate) style: Option<RStyle>,
    pub(crate) error_style: Option<RStyle>,
    pub(crate) warn_style: Option<RStyle>,
    pub(crate) info_style: Option<RStyle>,
    pub(crate) debug_style: Option<RStyle>,
    pub(crate) trace_style: Option<RStyle>,
}

impl TuiLoggerWidget {
    /// Build the ratatui widget with the given filter state embedded.
    pub(crate) fn to_ratatui<'a>(&self, state: &'a RTuiWidgetState) -> RTuiLoggerWidget<'a> {
        let mut w = RTuiLoggerWidget::default().state(state);
        if let Some(ref b) = self.block {
            w = w.block(b.to_ratatui());
        }
        if let Some(s) = self.style {
            w = w.style(s);
        }
        if let Some(s) = self.error_style {
            w = w.style_error(s);
        }
        if let Some(s) = self.warn_style {
            w = w.style_warn(s);
        }
        if let Some(s) = self.info_style {
            w = w.style_info(s);
        }
        if let Some(s) = self.debug_style {
            w = w.style_debug(s);
        }
        if let Some(s) = self.trace_style {
            w = w.style_trace(s);
        }
        w
    }
}

#[pymethods]
impl TuiLoggerWidget {
    #[new]
    pub fn new() -> Self {
        Self {
            block: None,
            style: None,
            error_style: None,
            warn_style: None,
            info_style: None,
            debug_style: None,
            trace_style: None,
        }
    }

    pub fn block(&self, block: Block) -> Self {
        let mut s = self.clone();
        s.block = Some(block);
        s
    }

    pub fn style(&self, style: &Style) -> Self {
        let mut s = self.clone();
        s.style = Some(style.inner);
        s
    }

    pub fn error_style(&self, style: &Style) -> Self {
        let mut s = self.clone();
        s.error_style = Some(style.inner);
        s
    }

    pub fn warn_style(&self, style: &Style) -> Self {
        let mut s = self.clone();
        s.warn_style = Some(style.inner);
        s
    }

    pub fn info_style(&self, style: &Style) -> Self {
        let mut s = self.clone();
        s.info_style = Some(style.inner);
        s
    }

    pub fn debug_style(&self, style: &Style) -> Self {
        let mut s = self.clone();
        s.debug_style = Some(style.inner);
        s
    }

    pub fn trace_style(&self, style: &Style) -> Self {
        let mut s = self.clone();
        s.trace_style = Some(style.inner);
        s
    }

    fn __repr__(&self) -> String {
        "TuiLoggerWidget".to_string()
    }
}

impl Default for TuiLoggerWidget {
    fn default() -> Self {
        Self::new()
    }
}

// ─── Registration ─────────────────────────────────────────────────────────────

pub fn register_logger(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<TuiLoggerWidget>()?;
    m.add_class::<TuiWidgetState>()?;
    m.add_function(wrap_pyfunction!(init_logger, m)?)?;
    m.add_function(wrap_pyfunction!(log_message, m)?)?;
    Ok(())
}
