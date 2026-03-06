// src/textarea/mod.rs
//! Python bindings for `tui-textarea` — a powerful multi-line text editor widget.
//!
//! Uses the `tui-textarea` crate (rhysd/tui-textarea v0.7.x) which targets
//! `ratatui = ">=0.23, <1"`.  ratatui 0.30 is within that range.
//!
//! # Quick-start
//! ```python
//! from pyratatui import TextArea, CursorMove, Terminal
//!
//! ta = TextArea.from_lines(["Hello", "World"])
//! ta.set_placeholder("Type here…")
//!
//! with Terminal() as term:
//!     while True:
//!         term.draw(lambda frame: frame.render_textarea(ta, frame.area))
//!         ev = term.poll_event(timeout_ms=50)
//!         if ev:
//!             if ev.code == "Esc": break
//!             ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)
//!
//! print("\n".join(ta.lines()))
//! ```

use pyo3::prelude::*;
use ratatui::layout::Rect as RRect;
use ratatui::style::Modifier as RModifier;
use ratatui::Frame as RFrame;
use tui_textarea::TextArea as TTextArea;

// ratatui_compat resolves to ratatui 0.29 — the SAME version that tui-textarea 0.7
// compiled against.  This lets us name the 0.29 types so we can bridge them via
// safe transmute (both 0.29 and 0.30 structs have identical memory layouts).
extern crate ratatui_compat;

use crate::style::Style;
use crate::widgets::Block;

// ── CursorMove ────────────────────────────────────────────────────────────────

/// Cursor movement command for `TextArea.move_cursor()`.
///
/// ```python
/// from pyratatui import TextArea, CursorMove
///
/// ta = TextArea()
/// ta.move_cursor(CursorMove.WordForward)
/// ta.move_cursor(CursorMove.Head)
/// ta.move_cursor(CursorMove.Bottom)
/// ```
#[pyclass(module = "pyratatui", eq, eq_int, from_py_object)]
#[derive(Clone, Debug, PartialEq)]
pub enum CursorMove {
    /// Move cursor one character forward (right).
    Forward,
    /// Move cursor one character backward (left).
    Back,
    /// Move cursor one line up.
    Up,
    /// Move cursor one line down.
    Down,
    /// Move cursor to the start of the next word.
    WordForward,
    /// Move cursor to the end of the current/next word.
    WordEnd,
    /// Move cursor to the start of the previous word.
    WordBack,
    /// Move cursor to the beginning of the current line.
    Head,
    /// Move cursor to the end of the current line.
    End,
    /// Move cursor to the first line (top).
    Top,
    /// Move cursor to the last line (bottom).
    Bottom,
    /// Move cursor to the first line of the visible viewport.
    ViewportTop,
    /// Move cursor to the middle line of the visible viewport.
    ViewportMiddle,
    /// Move cursor to the last line of the visible viewport.
    ViewportBottom,
    /// Move cursor to paragraph start.
    ParagraphBack,
    /// Move cursor to paragraph end.
    ParagraphForward,
}

impl CursorMove {
    pub(crate) fn to_tui(&self) -> tui_textarea::CursorMove {
        match self {
            CursorMove::Forward => tui_textarea::CursorMove::Forward,
            CursorMove::Back => tui_textarea::CursorMove::Back,
            CursorMove::Up => tui_textarea::CursorMove::Up,
            CursorMove::Down => tui_textarea::CursorMove::Down,
            CursorMove::WordForward => tui_textarea::CursorMove::WordForward,
            CursorMove::WordEnd => tui_textarea::CursorMove::WordEnd,
            CursorMove::WordBack => tui_textarea::CursorMove::WordBack,
            CursorMove::Head => tui_textarea::CursorMove::Head,
            CursorMove::End => tui_textarea::CursorMove::End,
            CursorMove::Top => tui_textarea::CursorMove::Top,
            CursorMove::Bottom => tui_textarea::CursorMove::Bottom,
            // ViewportTop/Middle/Bottom were removed from tui-textarea 0.7; map to nearest.
            CursorMove::ViewportTop => tui_textarea::CursorMove::Top,
            CursorMove::ViewportMiddle => tui_textarea::CursorMove::Top,
            CursorMove::ViewportBottom => tui_textarea::CursorMove::Bottom,
            CursorMove::ParagraphBack => tui_textarea::CursorMove::ParagraphBack,
            CursorMove::ParagraphForward => tui_textarea::CursorMove::ParagraphForward,
        }
    }
}

#[pymethods]
impl CursorMove {
    fn __repr__(&self) -> String {
        format!("CursorMove.{:?}", self)
    }
}

// ── Scrolling ─────────────────────────────────────────────────────────────────

/// Scroll amount for mouse scroll events passed to `TextArea.scroll()`.
#[pyclass(module = "pyratatui", eq, eq_int, from_py_object)]
#[derive(Clone, Debug, PartialEq)]
pub enum Scrolling {
    /// Scroll down by half a page.
    HalfPageDown,
    /// Scroll up by half a page.
    HalfPageUp,
    /// Scroll down by one page.
    PageDown,
    /// Scroll up by one page.
    PageUp,
    /// Scroll down by one line.
    DeltaDown,
    /// Scroll up by one line.
    DeltaUp,
}

impl Scrolling {
    pub(crate) fn to_tui(&self) -> tui_textarea::Scrolling {
        match self {
            Scrolling::HalfPageDown => tui_textarea::Scrolling::HalfPageDown,
            Scrolling::HalfPageUp => tui_textarea::Scrolling::HalfPageUp,
            Scrolling::PageDown => tui_textarea::Scrolling::PageDown,
            Scrolling::PageUp => tui_textarea::Scrolling::PageUp,
            // tui-textarea 0.7: `rows` field type is i16 (changed from i32).
            Scrolling::DeltaDown => tui_textarea::Scrolling::Delta {
                rows: 1_i16,
                cols: 0,
            },
            Scrolling::DeltaUp => tui_textarea::Scrolling::Delta {
                rows: -1_i16,
                cols: 0,
            },
        }
    }
}

#[pymethods]
impl Scrolling {
    fn __repr__(&self) -> String {
        format!("Scrolling.{:?}", self)
    }
}

// ── TextArea ──────────────────────────────────────────────────────────────────

/// A powerful multi-line text editor widget.
///
/// Uses `tui-textarea` (rhysd/tui-textarea) which is compatible with
/// ratatui >=0.23, covering ratatui 0.30.
///
/// # Creating a TextArea
/// ```python
/// from pyratatui import TextArea
///
/// ta = TextArea()                                # empty
/// ta = TextArea.from_lines(["Hello", "World"])   # pre-filled
/// ```
///
/// # Key input
/// ```python
/// ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)
/// ```
#[pyclass(module = "pyratatui", unsendable)]
pub struct TextArea {
    pub(crate) inner: TTextArea<'static>,
}

#[pymethods]
impl TextArea {
    /// Create an empty `TextArea`.
    #[new]
    pub fn new() -> Self {
        Self {
            inner: TTextArea::default(),
        }
    }

    /// Create a `TextArea` pre-filled with the given lines.
    #[staticmethod]
    pub fn from_lines(lines: Vec<String>) -> Self {
        Self {
            inner: TTextArea::new(lines),
        }
    }

    /// Process a key event using default Emacs-style bindings.
    ///
    /// Returns `True` if the event consumed the input (text was modified).
    pub fn input_key(&mut self, code: &str, ctrl: bool, alt: bool, shift: bool) -> bool {
        let key = py_key_to_tui(code);
        let input = tui_textarea::Input {
            key,
            ctrl,
            alt,
            shift,
        };
        self.inner.input(input)
    }

    /// Process a key event bypassing default shortcuts.
    pub fn input_without_shortcuts(
        &mut self,
        code: &str,
        ctrl: bool,
        alt: bool,
        shift: bool,
    ) -> bool {
        let key = py_key_to_tui(code);
        let input = tui_textarea::Input {
            key,
            ctrl,
            alt,
            shift,
        };
        self.inner.input_without_shortcuts(input)
    }

    pub fn insert_str(&mut self, s: &str) -> bool {
        self.inner.insert_str(s)
    }
    pub fn delete_char(&mut self) -> bool {
        self.inner.delete_char()
    }
    pub fn delete_next_char(&mut self) -> bool {
        self.inner.delete_next_char()
    }

    /// Insert a newline.  Returns `true` unconditionally (API unified in 0.7).
    pub fn insert_newline(&mut self) -> bool {
        self.inner.insert_newline();
        true
    }

    pub fn delete_line_by_end(&mut self) -> bool {
        self.inner.delete_line_by_end()
    }
    pub fn delete_line_by_head(&mut self) -> bool {
        self.inner.delete_line_by_head()
    }
    pub fn delete_word(&mut self) -> bool {
        self.inner.delete_word()
    }
    pub fn delete_next_word(&mut self) -> bool {
        self.inner.delete_next_word()
    }

    pub fn move_cursor(&mut self, m: &CursorMove) {
        self.inner.move_cursor(m.to_tui());
    }

    pub fn move_cursor_to(&mut self, row: usize, col: usize) {
        self.inner
            .move_cursor(tui_textarea::CursorMove::Jump(row as u16, col as u16));
    }

    pub fn scroll(&mut self, s: &Scrolling) {
        self.inner.scroll(s.to_tui());
    }

    pub fn undo(&mut self) -> bool {
        self.inner.undo()
    }
    pub fn redo(&mut self) -> bool {
        self.inner.redo()
    }
    pub fn paste(&mut self) -> bool {
        self.inner.paste()
    }

    pub fn start_selection(&mut self) {
        self.inner.start_selection();
    }
    pub fn cancel_selection(&mut self) {
        self.inner.cancel_selection();
    }
    pub fn cut(&mut self) -> bool {
        self.inner.cut()
    }
    pub fn copy(&mut self) {
        self.inner.copy();
    }

    pub fn lines(&self) -> Vec<String> {
        self.inner.lines().to_vec()
    }

    pub fn cursor(&self) -> (usize, usize) {
        self.inner.cursor()
    }

    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
    pub fn len(&self) -> usize {
        self.inner.lines().len()
    }

    pub fn set_block(&mut self, block: &Block) {
        // Bridge ratatui 0.30 Block → 0.29 Block via transmute (identical layouts).
        let new_block = block.to_ratatui();
        let compat: ratatui_compat::widgets::Block<'static> =
            unsafe { std::mem::transmute(new_block) };
        self.inner.set_block(compat);
    }

    pub fn set_cursor_style(&mut self, style: &Style) {
        let new_style = style.inner.add_modifier(RModifier::REVERSED);
        let compat: ratatui_compat::style::Style = unsafe { std::mem::transmute(new_style) };
        self.inner.set_cursor_style(compat);
    }

    pub fn set_cursor_line_style(&mut self, style: &Style) {
        let compat: ratatui_compat::style::Style = unsafe { std::mem::transmute(style.inner) };
        self.inner.set_cursor_line_style(compat);
    }

    pub fn set_line_number_style(&mut self, style: &Style) {
        let compat: ratatui_compat::style::Style = unsafe { std::mem::transmute(style.inner) };
        self.inner.set_line_number_style(compat);
    }

    pub fn remove_line_number(&mut self) {
        self.inner.remove_line_number();
    }

    pub fn set_placeholder_text(&mut self, text: &str) {
        self.inner.set_placeholder_text(text);
    }

    pub fn set_placeholder_style(&mut self, style: &Style) {
        let compat: ratatui_compat::style::Style = unsafe { std::mem::transmute(style.inner) };
        self.inner.set_placeholder_style(compat);
    }

    pub fn set_tab_length(&mut self, n: u8) {
        self.inner.set_tab_length(n);
    }
    pub fn set_hard_tab_indent(&mut self, en: bool) {
        self.inner.set_hard_tab_indent(en);
    }
    pub fn set_max_histories(&mut self, n: usize) {
        self.inner.set_max_histories(n);
    }

    pub fn selection_range(&self) -> Option<((usize, usize), (usize, usize))> {
        self.inner.selection_range()
    }

    fn __repr__(&self) -> String {
        let n = self.inner.lines().len();
        let preview = self.inner.lines().first().cloned().unwrap_or_default();
        format!(
            "TextArea(lines={}, cursor={:?}, first={:?})",
            n,
            self.inner.cursor(),
            preview
        )
    }
}

impl TextArea {
    /// Render into a ratatui frame (called by `Frame.render_textarea`).
    ///
    /// tui-textarea 0.7 implements `ratatui 0.29` Widget.  Our Frame is from
    /// ratatui 0.30.  Since both versions have identical Buffer/Rect layouts,
    /// we bridge via safe pointer transmutes.
    pub(crate) fn render_raw(&self, frame: &mut RFrame<'_>, area: RRect) {
        use ratatui_compat::widgets::Widget as CompatWidget;
        let buf = frame.buffer_mut();
        // SAFETY: ratatui 0.29 and 0.30 Rect/Buffer are layout-identical.
        let compat_area: ratatui_compat::layout::Rect = unsafe { std::mem::transmute(area) };
        let compat_buf: &mut ratatui_compat::buffer::Buffer =
            unsafe { &mut *(buf as *mut _ as *mut _) };
        CompatWidget::render(&self.inner, compat_area, compat_buf);
    }
}

// ── Key mapping helper ────────────────────────────────────────────────────────

fn py_key_to_tui(code: &str) -> tui_textarea::Key {
    use tui_textarea::Key;
    match code {
        "Enter" => Key::Enter,
        "Esc" => Key::Esc,
        "Backspace" => Key::Backspace,
        "Delete" => Key::Delete,
        "Tab" => Key::Tab,
        "BackTab" => Key::Char('\t'),
        "Up" => Key::Up,
        "Down" => Key::Down,
        "Left" => Key::Left,
        "Right" => Key::Right,
        "Home" => Key::Home,
        "End" => Key::End,
        "PageUp" => Key::PageUp,
        "PageDown" => Key::PageDown,
        "F1" => Key::F(1),
        "F2" => Key::F(2),
        "F3" => Key::F(3),
        "F4" => Key::F(4),
        "F5" => Key::F(5),
        "F6" => Key::F(6),
        "F7" => Key::F(7),
        "F8" => Key::F(8),
        "F9" => Key::F(9),
        "F10" => Key::F(10),
        "F11" => Key::F(11),
        "F12" => Key::F(12),
        s if s.chars().count() == 1 => Key::Char(s.chars().next().unwrap()),
        _ => Key::Null,
    }
}

// ── Module registration ───────────────────────────────────────────────────────

pub fn register_textarea(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CursorMove>()?;
    m.add_class::<Scrolling>()?;
    m.add_class::<TextArea>()?;
    Ok(())
}
