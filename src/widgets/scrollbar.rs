// src/widgets/scrollbar.rs
use crate::style::Style;
use pyo3::prelude::*;
use ratatui::widgets::{
    Scrollbar as RScrollbar, ScrollbarOrientation as RScrollbarOrientation,
    ScrollbarState as RScrollbarState,
};

/// Orientation of a scrollbar.
#[pyclass(module = "pyratatui", eq, eq_int, from_py_object)]
#[derive(Clone, Debug, PartialEq)]
pub enum ScrollbarOrientation {
    VerticalRight,
    VerticalLeft,
    HorizontalBottom,
    HorizontalTop,
}

impl ScrollbarOrientation {
    fn to_ratatui(&self) -> RScrollbarOrientation {
        match self {
            ScrollbarOrientation::VerticalRight => RScrollbarOrientation::VerticalRight,
            ScrollbarOrientation::VerticalLeft => RScrollbarOrientation::VerticalLeft,
            ScrollbarOrientation::HorizontalBottom => RScrollbarOrientation::HorizontalBottom,
            ScrollbarOrientation::HorizontalTop => RScrollbarOrientation::HorizontalTop,
        }
    }
}

/// Mutable scroll position state.
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct ScrollbarState {
    pub(crate) inner: RScrollbarState,
    pos: usize,
}

#[pymethods]
impl ScrollbarState {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: RScrollbarState::default(),
            pos: 0,
        }
    }

    pub fn content_length(&self, n: usize) -> ScrollbarState {
        let mut s = self.clone();
        s.inner = s.inner.content_length(n);
        s
    }
    /// Set the scroll position (builder style — returns new state).
    pub fn position(&self, p: usize) -> ScrollbarState {
        let mut s = self.clone();
        s.inner = s.inner.position(p);
        s.pos = p;
        s
    }
    pub fn scroll_next(&mut self) {
        self.inner.next();
        self.pos = self.pos.saturating_add(1);
    }
    pub fn scroll_prev(&mut self) {
        self.inner.prev();
        self.pos = self.pos.saturating_sub(1);
    }
    pub fn first(&mut self) {
        self.inner.first();
        self.pos = 0;
    }
    pub fn last(&mut self) {
        self.inner.last();
    }

    #[getter]
    pub fn get_position(&self) -> usize {
        self.pos
    }

    fn __repr__(&self) -> String {
        format!("ScrollbarState(pos={})", self.pos)
    }
}

/// A scroll indicator widget.
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct Scrollbar {
    orientation: ScrollbarOrientation,
    thumb_style: Option<Style>,
    track_style: Option<Style>,
    begin_style: Option<Style>,
    end_style: Option<Style>,
}

impl Scrollbar {
    pub(crate) fn to_ratatui(&self) -> RScrollbar<'static> {
        let mut s = RScrollbar::new(self.orientation.to_ratatui());
        if let Some(ref st) = self.thumb_style {
            s = s.thumb_style(st.inner);
        }
        if let Some(ref st) = self.track_style {
            s = s.track_style(st.inner);
        }
        if let Some(ref st) = self.begin_style {
            s = s.begin_style(st.inner);
        }
        if let Some(ref st) = self.end_style {
            s = s.end_style(st.inner);
        }
        s
    }
}

#[pymethods]
impl Scrollbar {
    #[new]
    #[pyo3(signature = (orientation=None))]
    pub fn new(orientation: Option<&ScrollbarOrientation>) -> Self {
        Self {
            orientation: orientation
                .cloned()
                .unwrap_or(ScrollbarOrientation::VerticalRight),
            thumb_style: None,
            track_style: None,
            begin_style: None,
            end_style: None,
        }
    }
    pub fn orientation(&self, o: &ScrollbarOrientation) -> Scrollbar {
        let mut s = self.clone();
        s.orientation = o.clone();
        s
    }
    pub fn thumb_style(&self, st: &Style) -> Scrollbar {
        let mut s = self.clone();
        s.thumb_style = Some(st.clone());
        s
    }
    pub fn track_style(&self, st: &Style) -> Scrollbar {
        let mut s = self.clone();
        s.track_style = Some(st.clone());
        s
    }
    pub fn begin_style(&self, st: &Style) -> Scrollbar {
        let mut s = self.clone();
        s.begin_style = Some(st.clone());
        s
    }
    pub fn end_style(&self, st: &Style) -> Scrollbar {
        let mut s = self.clone();
        s.end_style = Some(st.clone());
        s
    }
    fn __repr__(&self) -> String {
        "Scrollbar()".to_string()
    }
}

pub fn register_scrollbar(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<ScrollbarOrientation>()?;
    m.add_class::<ScrollbarState>()?;
    m.add_class::<Scrollbar>()?;
    Ok(())
}
