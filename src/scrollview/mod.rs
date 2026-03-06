// src/scrollview/mod.rs
//! Python bindings for `tui-scrollview` — a scrollable viewport widget.
//!
//! Official API (from docs.rs/tui-scrollview):
//!
//! ```rust
//! use tui_scrollview::{ScrollView, ScrollViewState};
//! use ratatui::layout::Size;
//!
//! let content_size = Size::new(100, 30);
//! let mut scroll_view = ScrollView::new(content_size);
//! // Render widgets INTO the virtual buffer:
//! scroll_view.render_widget(Paragraph::new("..."), area);
//! // Flush the visible portion to the terminal buffer:
//! scroll_view.render(area, buf, state);   // ← method on ScrollView, NOT trait
//! ```
//!
//! `ScrollViewState` helpers:
//! - `scroll_down_by(n)` / `scroll_up_by(n)` / `scroll_left_by(n)` / `scroll_right_by(n)`
//! - `scroll_to_top()` / `scroll_to_bottom()`
//! - `offset() → Position { x, y }`

use pyo3::prelude::*;
use ratatui::layout::{Rect as RRect, Size as RSize};
use ratatui::prelude::StatefulWidget;
use ratatui::text::{Line as RLine, Text as RText};
use ratatui::widgets::{Block as RBlock, Borders, Paragraph as RParagraph};
use ratatui::{buffer::Buffer as RBuffer, Frame as RFrame};
use tui_scrollview::{ScrollView as TScrollView, ScrollViewState as TScrollViewState};

// ── ScrollViewState ───────────────────────────────────────────────────────────

/// State for a `ScrollView` — tracks the current scroll offset.
///
/// ```python
/// from pyratatui import ScrollView, ScrollViewState
///
/// state = ScrollViewState()
///
/// def ui(frame):
///     sv = ScrollView.from_lines(lines, content_width=80)
///     frame.render_stateful_scrollview(sv, frame.area, state)
///
/// # Arrow key navigation:
/// state.scroll_down(1)
/// state.scroll_up(1)
/// state.scroll_to_top()
/// ```
#[pyclass(module = "pyratatui", unsendable)]
#[derive(Debug)]
pub struct ScrollViewState {
    pub(crate) inner: TScrollViewState,
}

#[pymethods]
impl ScrollViewState {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: TScrollViewState::default(),
        }
    }

    /// Scroll down by `n` lines.
    pub fn scroll_down(&mut self, n: u16) {
        for _ in 0..n {
            self.inner.scroll_down();
        }
    }
    /// Scroll up by `n` lines.
    pub fn scroll_up(&mut self, n: u16) {
        for _ in 0..n {
            self.inner.scroll_up();
        }
    }
    /// Scroll right by `n` columns.
    pub fn scroll_right(&mut self, n: u16) {
        for _ in 0..n {
            self.inner.scroll_right();
        }
    }
    /// Scroll left by `n` columns.
    pub fn scroll_left(&mut self, n: u16) {
        for _ in 0..n {
            self.inner.scroll_left();
        }
    }
    /// Scroll to the very top.
    pub fn scroll_to_top(&mut self) {
        self.inner.scroll_to_top();
    }
    /// Scroll to the very bottom.
    pub fn scroll_to_bottom(&mut self) {
        self.inner.scroll_to_bottom();
    }
    /// Reset to top-left origin.
    pub fn reset(&mut self) {
        self.inner = TScrollViewState::default();
    }

    /// Current offset as `(x, y)`.
    pub fn offset(&self) -> (u16, u16) {
        let pos = self.inner.offset();
        (pos.x, pos.y)
    }

    fn __repr__(&self) -> String {
        let (x, y) = self.offset();
        format!("ScrollViewState(offset=({x}, {y}))")
    }
}

// ── ScrollView ────────────────────────────────────────────────────────────────

/// A scrollable viewport widget.
///
/// Renders content larger than the visible area using a virtual buffer.
/// Combine with `ScrollViewState` to track the scroll position.
///
/// # Line-based content (most common)
/// ```python
/// from pyratatui import ScrollView, ScrollViewState
///
/// lines = [f"  {i:03d} │ " + "data " * 10 for i in range(200)]
/// state = ScrollViewState()
///
/// sv = ScrollView.from_lines(lines, content_width=80)
/// frame.render_stateful_scrollview(sv, frame.area, state)
/// ```
///
/// # Custom sections with optional titles
/// ```python
/// sv = ScrollView(content_width=80, content_height=50)
/// sv.add_paragraph("Header text", x=0, y=0, width=80, height=3)
/// sv.add_paragraph("Body text\nMore lines", x=0, y=3, width=80, height=20, title="Section A")
/// frame.render_stateful_scrollview(sv, frame.area, state)
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct ScrollView {
    pub(crate) content_width: u16,
    pub(crate) content_height: u16,
    pub(crate) sections: Vec<ScrollSection>,
}

#[derive(Clone, Debug)]
pub(crate) struct ScrollSection {
    pub text: String,
    pub x: u16,
    pub y: u16,
    pub width: u16,
    pub height: u16,
    pub title: Option<String>,
}

#[pymethods]
impl ScrollView {
    /// Create an empty `ScrollView` with the given virtual canvas size.
    #[new]
    pub fn new(content_width: u16, content_height: u16) -> Self {
        Self {
            content_width,
            content_height,
            sections: Vec::new(),
        }
    }

    /// Create a `ScrollView` from a plain list of text lines.
    ///
    /// The content height is set automatically to `len(lines)`.
    #[staticmethod]
    #[pyo3(signature = (lines, content_width = 80))]
    pub fn from_lines(lines: Vec<String>, content_width: u16) -> Self {
        let height = lines.len() as u16;
        let text = lines.join("\n");
        let mut sv = Self::new(content_width, height);
        sv.sections.push(ScrollSection {
            text,
            x: 0,
            y: 0,
            width: content_width,
            height,
            title: None,
        });
        sv
    }

    /// Add a text section at a given position in the virtual canvas.
    ///
    /// If `title` is given, the section is wrapped in a bordered block.
    #[pyo3(signature = (text, x=0, y=0, width=80, height=10, title=None))]
    pub fn add_paragraph(
        &mut self,
        text: &str,
        x: u16,
        y: u16,
        width: u16,
        height: u16,
        title: Option<String>,
    ) {
        self.sections.push(ScrollSection {
            text: text.to_string(),
            x,
            y,
            width,
            height,
            title,
        });
    }

    #[getter]
    pub fn content_width(&self) -> u16 {
        self.content_width
    }
    #[getter]
    pub fn content_height(&self) -> u16 {
        self.content_height
    }

    fn __repr__(&self) -> String {
        format!(
            "ScrollView({}×{}, sections={})",
            self.content_width,
            self.content_height,
            self.sections.len()
        )
    }
}

impl ScrollView {
    /// Render the `ScrollView` into a ratatui frame.
    ///
    /// tui-scrollview API:
    /// 1. `ScrollView::new(Size)` — create virtual canvas
    /// 2. `sv.render_widget(widget, area)` — paint widgets into it
    /// 3. `sv.render(area, buf, state)` — flush visible portion to terminal buffer
    pub(crate) fn render_into_frame(
        &self,
        frame: &mut RFrame<'_>,
        area: RRect,
        state: &mut ScrollViewState,
    ) {
        let size = RSize::new(self.content_width, self.content_height);
        let mut sv = TScrollView::new(size);

        for section in &self.sections {
            let sec_area = RRect::new(section.x, section.y, section.width, section.height);
            let text = build_text(&section.text);

            if let Some(ref title) = section.title {
                let block = RBlock::default()
                    .borders(Borders::ALL)
                    .title_top(title.as_str());
                sv.render_widget(RParagraph::new(text).block(block), sec_area);
            } else {
                sv.render_widget(RParagraph::new(text), sec_area);
            }
        }

        // `ScrollView::render(area, buf, state)` — this is a method on TScrollView,
        // NOT the StatefulWidget trait (the trait is implemented internally).
        let buf: &mut RBuffer = frame.buffer_mut();
        sv.render(area, buf, &mut state.inner);
    }
}

/// Convert a multi-line string to `Text<'static>`.
fn build_text(s: &str) -> RText<'static> {
    let lines: Vec<RLine<'static>> = s.lines().map(|l| RLine::raw(l.to_string())).collect();
    RText::from(lines)
}

// ── Module registration ───────────────────────────────────────────────────────

pub fn register_scrollview(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ScrollViewState>()?;
    m.add_class::<ScrollView>()?;
    Ok(())
}
