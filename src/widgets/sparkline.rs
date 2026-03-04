// src/widgets/sparkline.rs
use pyo3::prelude::*;
use ratatui::widgets::Sparkline as RSparkline;
use crate::style::Style;
use crate::widgets::block::Block;

/// A compact single-row sparkline chart.
///
/// ```python
/// from pyratatui import Sparkline, Style, Color
///
/// spark = (Sparkline()
///     .data([10, 20, 15, 35, 25, 40, 30])
///     .style(Style().fg(Color.green())))
/// ```
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct Sparkline {
    data: Vec<u64>,
    block: Option<Block>,
    max: Option<u64>,
    style: Option<Style>,
    bar_set: String,
    direction: String,
}

impl Sparkline {
    pub(crate) fn to_ratatui(&self) -> RSparkline<'static> {
        let mut s = RSparkline::default().data(self.data.clone());
        if let Some(ref b) = self.block { s = s.block(b.to_ratatui()); }
        if let Some(m) = self.max { s = s.max(m); }
        if let Some(ref st) = self.style { s = s.style(st.inner); }
        s
    }
}

#[pymethods]
impl Sparkline {
    #[new]
    pub fn new() -> Self {
        Self { data: vec![], block: None, max: None, style: None, bar_set: "braille".into(), direction: "left_to_right".into() }
    }
    pub fn data(&self, data: Vec<u64>) -> Sparkline { let mut s = self.clone(); s.data = data; s }
    pub fn block(&self, block: &Block) -> Sparkline { let mut s = self.clone(); s.block = Some(block.clone()); s }
    pub fn max(&self, m: u64) -> Sparkline { let mut s = self.clone(); s.max = Some(m); s }
    pub fn style(&self, style: &Style) -> Sparkline { let mut s = self.clone(); s.style = Some(style.clone()); s }
    fn __repr__(&self) -> String { format!("Sparkline(data_len={})", self.data.len()) }
}

pub fn register_sparkline(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Sparkline>()?;
    Ok(())
}
