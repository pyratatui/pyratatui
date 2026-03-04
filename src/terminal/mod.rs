// src/terminal/mod.rs
//! Python bindings for `Terminal` and `Frame`.
//!
//! This is the heart of pyratatui: `Terminal` owns the screen and drives the
//! render loop; `Frame` is passed into the draw callback each tick.

use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use std::io::{self, Stdout};

use crossterm::{
    event::{self, Event, KeyCode, KeyEvent, KeyEventKind, KeyModifiers},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};

use ratatui::{backend::CrosstermBackend, Frame as RFrame, Terminal as RTerminal};

use crate::effects::{Effect as PyEffect, EffectManager as PyEffectManager};
use crate::errors::{io_err_to_py, render_err_to_py};
use crate::layout::Rect;
use crate::widgets::{
    BarChart, Block, Clear, Gauge, LineGauge, List, ListState, Paragraph, Scrollbar,
    ScrollbarState, Sparkline, Table, TableState, Tabs,
};

// ─── KeyEvent wrapper ─────────────────────────────────────────────────────────

/// A keyboard event returned from `Terminal.poll_event()`.
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct PyKeyEvent {
    /// Key code as a string (e.g. "a", "Enter", "Esc", "Up", "F1").
    #[pyo3(get)]
    pub code: String,
    /// Whether Ctrl was held.
    #[pyo3(get)]
    pub ctrl: bool,
    /// Whether Alt was held.
    #[pyo3(get)]
    pub alt: bool,
    /// Whether Shift was held.
    #[pyo3(get)]
    pub shift: bool,
}

fn key_code_str(kc: &KeyCode) -> String {
    match kc {
        KeyCode::Char(c) => c.to_string(),
        KeyCode::Enter => "Enter".into(),
        KeyCode::Esc => "Esc".into(),
        KeyCode::Backspace => "Backspace".into(),
        KeyCode::Delete => "Delete".into(),
        KeyCode::Tab => "Tab".into(),
        KeyCode::BackTab => "BackTab".into(),
        KeyCode::Up => "Up".into(),
        KeyCode::Down => "Down".into(),
        KeyCode::Left => "Left".into(),
        KeyCode::Right => "Right".into(),
        KeyCode::Home => "Home".into(),
        KeyCode::End => "End".into(),
        KeyCode::PageUp => "PageUp".into(),
        KeyCode::PageDown => "PageDown".into(),
        KeyCode::Insert => "Insert".into(),
        KeyCode::F(n) => format!("F{}", n),
        KeyCode::Null => "Null".into(),
        _ => "Unknown".into(),
    }
}

#[pymethods]
impl PyKeyEvent {
    fn __repr__(&self) -> String {
        format!(
            "KeyEvent(code={:?}, ctrl={}, alt={}, shift={})",
            self.code, self.ctrl, self.alt, self.shift
        )
    }
}

// ─── Frame ────────────────────────────────────────────────────────────────────

/// A single render frame passed to the draw callback.
///
/// Use the `render_*` methods to draw widgets onto the screen.
///
/// ```python
/// def ui(frame):
///     area = frame.area
///     frame.render_widget(
///         Paragraph.from_string("Hello!").block(Block().bordered()),
///         area
///     )
/// ```
///
/// **Note:** `Frame` is only valid inside the `draw` callback. Do not store
/// references to it.
#[pyclass(module = "pyratatui", unsendable)]
pub struct Frame {
    // We use a raw pointer here because Frame borrows the terminal which
    // lives on the Rust side; the pointer is only dereferenced inside the
    // draw callback and is guaranteed valid.
    ptr: *mut RFrame<'static>,
}

unsafe impl Send for Frame {}

impl Frame {
    fn get(&mut self) -> &mut RFrame<'static> {
        unsafe { &mut *self.ptr }
    }
}

#[pymethods]
impl Frame {
    /// The full terminal area available for this frame.
    #[getter]
    pub fn area(&mut self) -> Rect {
        Rect {
            inner: self.get().area(),
        }
    }

    /// The full terminal size (alias for `area`).
    #[getter]
    pub fn size(&mut self) -> Rect {
        self.area()
    }

    /// Render a widget into the given area.
    ///
    /// Accepts: `Block`, `Paragraph`, `Gauge`, `LineGauge`, `BarChart`,
    /// `Sparkline`, `Clear`, `Scrollbar`, `Tabs`.
    pub fn render_widget(&mut self, widget: &Bound<'_, PyAny>, area: &Rect) -> PyResult<()> {
        let frame = self.get();
        let a = area.inner;

        macro_rules! try_widget {
            ($T:ty, $to_rat:ident) => {
                if let Ok(w) = widget.extract::<PyRef<$T>>() {
                    frame.render_widget(w.$to_rat(), a);
                    return Ok(());
                }
            };
        }

        try_widget!(Block, to_ratatui);
        try_widget!(Paragraph, to_ratatui);
        try_widget!(Gauge, to_ratatui);
        try_widget!(LineGauge, to_ratatui);
        try_widget!(BarChart, to_ratatui);
        try_widget!(Sparkline, to_ratatui);
        try_widget!(Clear, to_ratatui);
        try_widget!(Tabs, to_ratatui);

        // Handle List separately (stateless render)
        if let Ok(w) = widget.extract::<PyRef<List>>() {
            frame.render_widget(w.to_ratatui(), a);
            return Ok(());
        }
        // Handle Table separately
        if let Ok(w) = widget.extract::<PyRef<Table>>() {
            frame.render_widget(w.to_ratatui(), a);
            return Ok(());
        }

        Err(render_err_to_py(format!(
            "Unknown widget type: {}",
            widget
                .get_type()
                .qualname()
                .map(|s| s.to_string())
                .unwrap_or_else(|_| "?".to_string())
        )))
    }

    /// Render a `List` with mutable selection state.
    pub fn render_stateful_list(
        &mut self,
        widget: &List,
        area: &Rect,
        state: &mut ListState,
    ) -> PyResult<()> {
        self.get()
            .render_stateful_widget(widget.to_ratatui(), area.inner, &mut state.inner);
        Ok(())
    }

    /// Render a `Table` with mutable selection state.
    pub fn render_stateful_table(
        &mut self,
        widget: &Table,
        area: &Rect,
        state: &mut TableState,
    ) -> PyResult<()> {
        self.get()
            .render_stateful_widget(widget.to_ratatui(), area.inner, &mut state.inner);
        Ok(())
    }

    /// Render a `Scrollbar` with its scroll state.
    pub fn render_stateful_scrollbar(
        &mut self,
        widget: &Scrollbar,
        area: &Rect,
        state: &mut ScrollbarState,
    ) -> PyResult<()> {
        self.get()
            .render_stateful_widget(widget.to_ratatui(), area.inner, &mut state.inner);
        Ok(())
    }

    fn __repr__(&self) -> String {
        "Frame(<active>)".to_string()
    }

    /// Apply a TachyonFX `Effect` to this frame's buffer.
    ///
    /// Call **after** all `render_widget` calls — effects transform already-rendered cells.
    pub fn apply_effect(&mut self, effect: &mut PyEffect, elapsed_ms: u64, area: &Rect) {
        use tachyonfx::Shader;
        let dur: tachyonfx::Duration = std::time::Duration::from_millis(elapsed_ms).into();
        let buf = unsafe { &mut *self.buffer_mut_ptr() };
        effect.inner.process(dur, buf, area.inner);
    }

    /// Apply an `EffectManager` to this frame's buffer.
    ///
    /// Advances all managed effects and removes completed ones.
    /// Call **after** all `render_widget` calls.
    pub fn apply_effect_manager(
        &mut self,
        manager: &mut PyEffectManager,
        elapsed_ms: u64,
        area: &Rect,
    ) {
        let buf = unsafe { &mut *self.buffer_mut_ptr() };
        manager.process_raw(elapsed_ms, buf, area.inner);
    }
}

impl Frame {
    // Called from the effect pipeline — safe only inside draw callback.
    pub(crate) fn buffer_mut_ptr(&mut self) -> *mut ratatui::buffer::Buffer {
        self.get().buffer_mut() as *mut _
    }
}

// ─── Terminal ─────────────────────────────────────────────────────────────────

type RatTerminal = RTerminal<CrosstermBackend<Stdout>>;

/// The main terminal driver.
///
/// `Terminal` initialises the crossterm backend, enters alternate screen mode,
/// enables raw input, and drives the render loop.
///
/// **Sync usage:**
///
/// ```python
/// from pyratatui import Terminal, Paragraph, Text
///
/// with Terminal() as term:
///     while True:
///         def ui(frame):
///             frame.render_widget(
///                 Paragraph.from_string("Hello! Press q to quit."),
///                 frame.area
///             )
///         term.draw(ui)
///         ev = term.poll_event(timeout_ms=100)
///         if ev and ev.code == "q":
///             break
/// ```
///
/// **Async usage:**
///
/// ```python
/// import asyncio
/// from pyratatui import Terminal, Paragraph
///
/// async def main():
///     async with Terminal() as term:
///         for _ in range(50):
///             def ui(frame):
///                 frame.render_widget(Paragraph.from_string("Async!"), frame.area)
///             term.draw(ui)
///             await asyncio.sleep(0.05)
///
/// asyncio.run(main())
/// ```
#[pyclass(module = "pyratatui", unsendable)]
pub struct Terminal {
    inner: Option<RatTerminal>,
    entered: bool,
}

#[pymethods]
impl Terminal {
    /// Create a new `Terminal` instance (does NOT initialise the screen yet).
    ///
    /// Call `__enter__` (or use `with Terminal() as t:`) to initialise.
    #[new]
    pub fn new() -> PyResult<Self> {
        Ok(Self {
            inner: None,
            entered: false,
        })
    }

    // ── Context manager ──────────────────────────────────────────────────────

    /// Initialise the terminal: enable raw mode, enter alternate screen.
    pub fn __enter__(mut slf: PyRefMut<'_, Self>) -> PyResult<PyRefMut<'_, Self>> {
        enable_raw_mode().map_err(io_err_to_py)?;
        let mut stdout = io::stdout();
        execute!(stdout, EnterAlternateScreen).map_err(io_err_to_py)?;
        let backend = CrosstermBackend::new(io::stdout());
        let terminal = RTerminal::new(backend).map_err(io_err_to_py)?;
        slf.inner = Some(terminal);
        slf.entered = true;
        Ok(slf)
    }

    /// Restore the terminal: leave alternate screen, disable raw mode.
    pub fn __exit__(
        &mut self,
        _exc_type: &Bound<'_, PyAny>,
        _exc_val: &Bound<'_, PyAny>,
        _exc_tb: &Bound<'_, PyAny>,
    ) -> PyResult<bool> {
        self.restore()?;
        Ok(false) // do not suppress exceptions
    }

    /// Manually restore the terminal (called automatically by `__exit__`).
    pub fn restore(&mut self) -> PyResult<()> {
        if self.entered {
            disable_raw_mode().map_err(io_err_to_py)?;
            execute!(io::stdout(), LeaveAlternateScreen).map_err(io_err_to_py)?;
            self.entered = false;
        }
        Ok(())
    }

    // ── Drawing ──────────────────────────────────────────────────────────────

    /// Call `draw_fn(frame)` to render one frame.
    ///
    /// `draw_fn` receives a `Frame` object and should call `frame.render_widget(...)`.
    pub fn draw(&mut self, draw_fn: &Bound<'_, PyAny>) -> PyResult<()> {
        let term = self.inner.as_mut().ok_or_else(|| {
            PyRuntimeError::new_err("Terminal not initialised — use `with Terminal() as t:`")
        })?;

        // Safety: the Frame pointer is only used inside this closure, which
        // completes before `draw` returns, so the reference is valid.
        term.draw(|frame| {
            let py_frame = Frame {
                ptr: frame as *mut RFrame<'_> as *mut RFrame<'static>,
            };
            Python::with_gil(|py| {
                if let Ok(obj) = Py::new(py, py_frame) {
                    let _ = draw_fn.call1((obj,));
                }
            });
        })
        .map_err(io_err_to_py)?;

        Ok(())
    }

    // ── Events ───────────────────────────────────────────────────────────────

    /// Poll for a keyboard event.
    ///
    /// Args:
    ///     timeout_ms: Milliseconds to wait. 0 = non-blocking.
    ///
    /// Returns:
    ///     A `KeyEvent` if a key was pressed, otherwise `None`.
    #[pyo3(signature = (timeout_ms=0))]
    pub fn poll_event(&self, timeout_ms: u64) -> PyResult<Option<PyKeyEvent>> {
        let timeout = std::time::Duration::from_millis(timeout_ms);
        if event::poll(timeout).map_err(io_err_to_py)? {
            match event::read().map_err(io_err_to_py)? {
                Event::Key(KeyEvent {
                    code,
                    modifiers,
                    kind: KeyEventKind::Press,
                    ..
                }) => {
                    return Ok(Some(PyKeyEvent {
                        code: key_code_str(&code),
                        ctrl: modifiers.contains(KeyModifiers::CONTROL),
                        alt: modifiers.contains(KeyModifiers::ALT),
                        shift: modifiers.contains(KeyModifiers::SHIFT),
                    }));
                }
                _ => {}
            }
        }
        Ok(None)
    }

    // ── Sizing ───────────────────────────────────────────────────────────────

    /// The current terminal area.
    pub fn area(&mut self) -> PyResult<Rect> {
        let term = self
            .inner
            .as_mut()
            .ok_or_else(|| PyRuntimeError::new_err("Terminal not initialised"))?;
        Ok(Rect {
            inner: term.get_frame().area(),
        })
    }

    /// Force a full redraw on the next `draw()` call.
    pub fn clear(&mut self) -> PyResult<()> {
        let term = self
            .inner
            .as_mut()
            .ok_or_else(|| PyRuntimeError::new_err("Terminal not initialised"))?;
        term.clear().map_err(io_err_to_py)
    }

    /// Hide the cursor.
    pub fn hide_cursor(&mut self) -> PyResult<()> {
        let term = self
            .inner
            .as_mut()
            .ok_or_else(|| PyRuntimeError::new_err("Terminal not initialised"))?;
        term.hide_cursor().map_err(io_err_to_py)
    }

    /// Show the cursor.
    pub fn show_cursor(&mut self) -> PyResult<()> {
        let term = self
            .inner
            .as_mut()
            .ok_or_else(|| PyRuntimeError::new_err("Terminal not initialised"))?;
        term.show_cursor().map_err(io_err_to_py)
    }

    // ── Async helpers ─────────────────────────────────────────────────────────

    /// Async context manager entry (returns self).
    pub fn __aenter__<'a>(
        mut slf: PyRefMut<'a, Self>,
        _py: Python<'_>,
    ) -> PyResult<PyRefMut<'a, Self>> {
        enable_raw_mode().map_err(io_err_to_py)?;
        execute!(io::stdout(), EnterAlternateScreen).map_err(io_err_to_py)?;
        let backend = CrosstermBackend::new(io::stdout());
        let terminal = RTerminal::new(backend).map_err(io_err_to_py)?;
        slf.inner = Some(terminal);
        slf.entered = true;
        Ok(slf)
    }

    /// Async context manager exit (restores terminal).
    pub fn __aexit__(
        &mut self,
        py: Python<'_>,
        _exc_type: &Bound<'_, PyAny>,
        _exc_val: &Bound<'_, PyAny>,
        _exc_tb: &Bound<'_, PyAny>,
    ) -> PyResult<PyObject> {
        self.restore()?;
        Ok(py.None())
    }

    fn __repr__(&self) -> String {
        format!("Terminal(active={})", self.entered)
    }
}

pub fn register_terminal(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Terminal>()?;
    m.add_class::<Frame>()?;
    m.add_class::<PyKeyEvent>()?;
    Ok(())
}
