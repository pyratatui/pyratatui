// src/widgets/mod.rs
//! Python bindings for all ratatui built-in widgets.
//!
//! Each widget type lives in its own sub-module to keep things manageable.

use pyo3::prelude::*;

mod block;
mod paragraph;
mod list;
mod table;
mod gauge;
mod barchart;
mod sparkline;
mod clear;
mod canvas_widget;
mod scrollbar;
mod tabs;

pub use block::Block;
pub use paragraph::Paragraph;
#[allow(unused_imports)]
pub use list::{List, ListItem, ListState, ListDirection};
#[allow(unused_imports)]
pub use table::{Table, TableState, Cell, Row};
pub use gauge::{Gauge, LineGauge};
#[allow(unused_imports)]
pub use barchart::{BarChart, Bar, BarGroup};
pub use sparkline::Sparkline;
pub use clear::Clear;
#[allow(unused_imports)]
pub use scrollbar::{Scrollbar, ScrollbarState, ScrollbarOrientation};
pub use tabs::Tabs;

pub fn register_widgets(py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    block::register_block(py, m)?;
    paragraph::register_paragraph(py, m)?;
    list::register_list(py, m)?;
    table::register_table(py, m)?;
    gauge::register_gauge(py, m)?;
    barchart::register_barchart(py, m)?;
    sparkline::register_sparkline(py, m)?;
    clear::register_clear(py, m)?;
    scrollbar::register_scrollbar(py, m)?;
    tabs::register_tabs(py, m)?;
    Ok(())
}
