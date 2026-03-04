// src/widgets/table.rs
//! Python bindings for `Table`, `Row`, `Cell`, and `TableState`.

use pyo3::prelude::*;
use ratatui::layout::Constraint as RConstraint;
use ratatui::widgets::{Cell as RCell, Row as RRow, Table as RTable, TableState as RTableState};

use crate::layout::Constraint;
use crate::style::Style;
use crate::text::Text;
use crate::widgets::block::Block;

/// A single styled cell in a table row.
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct Cell {
    text: Text,
    style: Option<Style>,
}

impl Cell {
    pub(crate) fn to_ratatui(&self) -> RCell<'static> {
        let mut c = RCell::new(self.text.to_ratatui());
        if let Some(ref s) = self.style {
            c = c.style(s.inner);
        }
        c
    }
}

#[pymethods]
impl Cell {
    #[new]
    #[pyo3(signature = (text, style=None))]
    pub fn new(text: &str, style: Option<&Style>) -> Self {
        Self {
            text: Text::from_string(text),
            style: style.cloned(),
        }
    }

    pub fn style(&self, style: &Style) -> Cell {
        let mut c = self.clone();
        c.style = Some(style.clone());
        c
    }

    fn __repr__(&self) -> String {
        format!("Cell(width={})", self.text.width())
    }
}

/// A row of cells in a table.
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct Row {
    cells: Vec<Cell>,
    style: Option<Style>,
    height: u16,
}

impl Row {
    pub(crate) fn to_ratatui(&self) -> RRow<'static> {
        let cells: Vec<RCell<'static>> = self.cells.iter().map(|c| c.to_ratatui()).collect();
        let mut row = RRow::new(cells).height(self.height);
        if let Some(ref s) = self.style {
            row = row.style(s.inner);
        }
        row
    }
}

#[pymethods]
impl Row {
    #[new]
    pub fn new(cells: Vec<PyRef<Cell>>) -> Self {
        Self {
            cells: cells.iter().map(|c| (**c).clone()).collect(),
            style: None,
            height: 1,
        }
    }

    /// Convenience: create a row from plain strings.
    #[staticmethod]
    pub fn from_strings(texts: Vec<String>) -> Row {
        Row {
            cells: texts.iter().map(|t| Cell::new(t, None)).collect(),
            style: None,
            height: 1,
        }
    }

    pub fn style(&self, style: &Style) -> Row {
        let mut r = self.clone();
        r.style = Some(style.clone());
        r
    }
    pub fn height(&self, height: u16) -> Row {
        let mut r = self.clone();
        r.height = height;
        r
    }

    fn __repr__(&self) -> String {
        format!("Row(cells={})", self.cells.len())
    }
}

/// Mutable selection state for a `Table`.
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct TableState {
    pub(crate) inner: RTableState,
}

#[pymethods]
impl TableState {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: RTableState::default(),
        }
    }

    #[pyo3(signature = (index=None))]
    pub fn select(&mut self, index: Option<usize>) {
        self.inner.select(index);
    }

    pub fn select_next(&mut self) {
        self.inner.select_next();
    }
    pub fn select_previous(&mut self) {
        self.inner.select_previous();
    }
    pub fn select_first(&mut self) {
        self.inner.select_first();
    }
    pub fn select_last(&mut self) {
        self.inner.select_last();
    }

    #[getter]
    pub fn selected(&self) -> Option<usize> {
        self.inner.selected()
    }

    #[getter]
    pub fn offset(&self) -> usize {
        self.inner.offset()
    }
}

/// A data grid widget with headers and selectable rows.
///
/// ```python
/// from pyratatui import Table, Row, Cell, TableState, Constraint, Style, Color
///
/// table = (Table(
///     rows=[Row.from_strings(["Alice", "Engineer", "Berlin"])],
///     header=Row.from_strings(["Name", "Role", "City"]).style(Style().bold()),
///     widths=[Constraint.percentage(30), Constraint.fill(1), Constraint.percentage(30)],
/// )
/// .block(Block().bordered().title("Staff"))
/// .highlight_style(Style().fg(Color.cyan())))
///
/// state = TableState()
/// state.select(0)
/// ```
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct Table {
    rows: Vec<Row>,
    header: Option<Row>,
    footer: Option<Row>,
    widths: Vec<Constraint>,
    block: Option<Block>,
    style: Option<Style>,
    highlight_style: Option<Style>,
    highlight_symbol: Option<String>,
    column_spacing: u16,
}

impl Table {
    pub(crate) fn to_ratatui(&self) -> RTable<'static> {
        let rows: Vec<RRow<'static>> = self.rows.iter().map(|r| r.to_ratatui()).collect();
        let widths: Vec<RConstraint> = self.widths.iter().map(|c| c.inner).collect();

        let mut tbl = RTable::new(rows, widths);

        if let Some(ref h) = self.header {
            tbl = tbl.header(h.to_ratatui());
        }
        if let Some(ref f) = self.footer {
            tbl = tbl.footer(f.to_ratatui());
        }
        if let Some(ref b) = self.block {
            tbl = tbl.block(b.to_ratatui());
        }
        if let Some(ref s) = self.style {
            tbl = tbl.style(s.inner);
        }
        if let Some(ref s) = self.highlight_style {
            tbl = tbl.row_highlight_style(s.inner);
        }
        if let Some(ref sym) = self.highlight_symbol {
            tbl = tbl.highlight_symbol(sym.clone());
        }
        tbl = tbl.column_spacing(self.column_spacing);
        tbl
    }
}

#[pymethods]
impl Table {
    #[new]
    #[pyo3(signature = (rows, widths, header=None))]
    pub fn new(
        rows: Vec<PyRef<Row>>,
        widths: Vec<PyRef<Constraint>>,
        header: Option<&Row>,
    ) -> Self {
        Self {
            rows: rows.iter().map(|r| (**r).clone()).collect(),
            header: header.cloned(),
            footer: None,
            widths: widths.iter().map(|c| (**c).clone()).collect(),
            block: None,
            style: None,
            highlight_style: None,
            highlight_symbol: None,
            column_spacing: 1,
        }
    }

    pub fn block(&self, block: &Block) -> Table {
        let mut t = self.clone();
        t.block = Some(block.clone());
        t
    }
    pub fn style(&self, style: &Style) -> Table {
        let mut t = self.clone();
        t.style = Some(style.clone());
        t
    }
    pub fn highlight_style(&self, style: &Style) -> Table {
        let mut t = self.clone();
        t.highlight_style = Some(style.clone());
        t
    }
    pub fn highlight_symbol(&self, sym: &str) -> Table {
        let mut t = self.clone();
        t.highlight_symbol = Some(sym.to_string());
        t
    }
    pub fn column_spacing(&self, n: u16) -> Table {
        let mut t = self.clone();
        t.column_spacing = n;
        t
    }
    pub fn footer(&self, row: &Row) -> Table {
        let mut t = self.clone();
        t.footer = Some(row.clone());
        t
    }

    fn __repr__(&self) -> String {
        format!(
            "Table(rows={}, cols={})",
            self.rows.len(),
            self.widths.len()
        )
    }
}

pub fn register_table(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Cell>()?;
    m.add_class::<Row>()?;
    m.add_class::<TableState>()?;
    m.add_class::<Table>()?;
    Ok(())
}
