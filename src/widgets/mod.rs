// src/widgets/mod.rs
//! Python bindings for all ratatui built-in widgets.
//!
//! Each widget type lives in its own sub-module to keep things manageable.

use pyo3::prelude::*;

mod barchart;
mod block;
pub mod calendar;
mod canvas_widget;
mod clear;
mod gauge;
mod list;
mod paragraph;
mod scrollbar;
mod sparkline;
mod table;
mod tabs;

#[allow(unused_imports)]
pub use barchart::{Bar, BarChart, BarGroup};
pub use block::Block;
pub use calendar::Monthly;
pub use clear::Clear;
pub use gauge::{Gauge, LineGauge};
#[allow(unused_imports)]
pub use list::{List, ListDirection, ListItem, ListState};
pub use paragraph::Paragraph;
#[allow(unused_imports)]
pub use scrollbar::{Scrollbar, ScrollbarOrientation, ScrollbarState};
pub use sparkline::Sparkline;
#[allow(unused_imports)]
pub use table::{Cell, Row, Table, TableState};
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
    canvas_widget::register_canvas(py, m)?;
    calendar::register_calendar(py, m)?;
    Ok(())
}
