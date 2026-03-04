// src/layout/mod.rs
//! Python bindings for ratatui's layout primitives.
//!
//! Exposes:
//! - `Rect`       — a rectangular area (x, y, width, height)
//! - `Constraint` — a sizing rule for layout children
//! - `Direction`  — horizontal or vertical split direction
//! - `Layout`     — splits a `Rect` into child `Rect`s according to constraints
//! - `Margin`     — inner padding applied to a `Rect`
//! - `Alignment`  — horizontal text/widget alignment
//! - `Padding`    — per-edge padding

use pyo3::prelude::*;
use ratatui::layout::{
    Constraint as RConstraint,
    Direction as RDirection,
    Layout as RLayout,
    Rect as RRect,
    Margin as RMargin,
    Alignment as RAlignment,
};

use crate::errors::layout_err_to_py;

// ─── Rect ─────────────────────────────────────────────────────────────────────

/// A rectangular region on the terminal screen.
///
/// ```python
/// from pyratatui import Rect
///
/// r = Rect(0, 0, 80, 24)
/// inner = r.inner(1, 1)  # shrink by margin
/// ```
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug, Copy)]
pub struct Rect {
    pub(crate) inner: RRect,
}

#[pymethods]
impl Rect {
    /// Create a new Rect.
    ///
    /// Args:
    ///     x: Left column (0-based).
    ///     y: Top row (0-based).
    ///     width: Width in columns.
    ///     height: Height in rows.
    #[new]
    pub fn new(x: u16, y: u16, width: u16, height: u16) -> Self {
        Self { inner: RRect { x, y, width, height } }
    }

    #[getter] pub fn x(&self) -> u16 { self.inner.x }
    #[getter] pub fn y(&self) -> u16 { self.inner.y }
    #[getter] pub fn width(&self) -> u16 { self.inner.width }
    #[getter] pub fn height(&self) -> u16 { self.inner.height }

    /// The column just past the right edge.
    #[getter] pub fn right(&self) -> u16 { self.inner.right() }
    /// The row just past the bottom edge.
    #[getter] pub fn bottom(&self) -> u16 { self.inner.bottom() }
    /// The left column (alias for `x`).
    #[getter] pub fn left(&self) -> u16 { self.inner.left() }
    /// The top row (alias for `y`).
    #[getter] pub fn top(&self) -> u16 { self.inner.top() }

    /// Area in cells (width × height).
    pub fn area(&self) -> u32 { self.inner.area() }

    /// Whether the area is zero.
    pub fn is_empty(&self) -> bool { self.inner.is_empty() }

    /// Return the rect shrunk by the given horizontal and vertical margins.
    ///
    /// Args:
    ///     horizontal: Columns to remove from each side.
    ///     vertical:   Rows to remove from top and bottom.
    #[pyo3(signature = (horizontal=1, vertical=1))]
    pub fn inner(&self, horizontal: u16, vertical: u16) -> Rect {
        let margin = RMargin { horizontal, vertical };
        Rect { inner: self.inner.inner(margin) }
    }

    /// Return whether `other` is fully contained within `self`.
    pub fn contains(&self, other: &Rect) -> bool {
        let s = self.inner;
        let o = other.inner;
        o.x >= s.x
            && o.y >= s.y
            && (o.x + o.width)  <= (s.x + s.width)
            && (o.y + o.height) <= (s.y + s.height)
    }

    /// Return the intersection of `self` and `other`, or `None` if they don't overlap.
    pub fn intersection(&self, other: &Rect) -> Option<Rect> {
        let i = self.inner.intersection(other.inner);
        if i.is_empty() { None } else { Some(Rect { inner: i }) }
    }

    /// Return the union (bounding box) of `self` and `other`.
    pub fn union(&self, other: &Rect) -> Rect {
        Rect { inner: self.inner.union(other.inner) }
    }

    fn __repr__(&self) -> String {
        format!("Rect(x={}, y={}, width={}, height={})",
            self.inner.x, self.inner.y, self.inner.width, self.inner.height)
    }

    fn __eq__(&self, other: &Rect) -> bool { self.inner == other.inner }
}

// ─── Constraint ───────────────────────────────────────────────────────────────

/// A sizing rule for layout children.
///
/// ```python
/// from pyratatui import Constraint
///
/// fixed  = Constraint.length(20)
/// pct    = Constraint.percentage(50)
/// fill   = Constraint.fill(1)
/// minc   = Constraint.min(10)
/// maxc   = Constraint.max(40)
/// ratio  = Constraint.ratio(1, 3)
/// ```
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct Constraint {
    pub(crate) inner: RConstraint,
}

#[pymethods]
impl Constraint {
    /// A fixed size in terminal cells.
    #[staticmethod] pub fn length(n: u16) -> Self { Self { inner: RConstraint::Length(n) } }

    /// A percentage of the parent area (0-100).
    #[staticmethod] pub fn percentage(pct: u16) -> Self { Self { inner: RConstraint::Percentage(pct) } }

    /// Fill remaining space proportionally with a weight factor.
    #[staticmethod] pub fn fill(n: u16) -> Self { Self { inner: RConstraint::Fill(n) } }

    /// At least `n` cells.
    #[staticmethod] pub fn min(n: u16) -> Self { Self { inner: RConstraint::Min(n) } }

    /// At most `n` cells.
    #[staticmethod] pub fn max(n: u16) -> Self { Self { inner: RConstraint::Max(n) } }

    /// A ratio of `numerator`:`denominator`.
    #[staticmethod]
    pub fn ratio(numerator: u32, denominator: u32) -> Self {
        Self { inner: RConstraint::Ratio(numerator, denominator) }
    }

    fn __repr__(&self) -> String {
        format!("Constraint({:?})", self.inner)
    }
}

// ─── Direction ────────────────────────────────────────────────────────────────

/// The axis along which a layout splits its area.
#[pyclass(module = "pyratatui", eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum Direction {
    /// Split left → right.
    Horizontal,
    /// Split top → bottom.
    Vertical,
}

impl Direction {
    pub(crate) fn to_ratatui(&self) -> RDirection {
        match self {
            Direction::Horizontal => RDirection::Horizontal,
            Direction::Vertical   => RDirection::Vertical,
        }
    }
}

// ─── Alignment ────────────────────────────────────────────────────────────────

/// Horizontal alignment for text and widgets.
#[pyclass(module = "pyratatui", eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum Alignment {
    Left,
    Center,
    Right,
}

impl Alignment {
    pub(crate) fn to_ratatui(&self) -> RAlignment {
        match self {
            Alignment::Left   => RAlignment::Left,
            Alignment::Center => RAlignment::Center,
            Alignment::Right  => RAlignment::Right,
        }
    }
}

// ─── Layout ───────────────────────────────────────────────────────────────────

/// A layout engine that splits a `Rect` into child `Rect`s.
///
/// ```python
/// from pyratatui import Layout, Constraint, Direction, Rect
///
/// area = Rect(0, 0, 80, 24)
/// chunks = (Layout()
///     .direction(Direction.Vertical)
///     .constraints([Constraint.length(3), Constraint.fill(1), Constraint.length(1)])
///     .split(area))
/// header, body, footer = chunks
/// ```
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct Layout {
    constraints: Vec<Constraint>,
    direction: Direction,
    margin: u16,
    spacing: u16,
    flex: String,
}

#[pymethods]
impl Layout {
    #[new]
    pub fn new() -> Self {
        Self {
            constraints: vec![],
            direction: Direction::Vertical,
            margin: 0,
            spacing: 0,
            flex: "start".into(),
        }
    }

    /// Set the list of sizing constraints.
    pub fn constraints(&self, constraints: Vec<PyRef<Constraint>>) -> Layout {
        let mut l = self.clone();
        l.constraints = constraints.iter().map(|c| (**c).clone()).collect();
        l
    }

    /// Set the split direction.
    pub fn direction(&self, direction: &Direction) -> Layout {
        let mut l = self.clone();
        l.direction = direction.clone();
        l
    }

    /// Apply a uniform margin on all sides.
    pub fn margin(&self, margin: u16) -> Layout {
        let mut l = self.clone();
        l.margin = margin;
        l
    }

    /// Gap between child slots.
    pub fn spacing(&self, spacing: u16) -> Layout {
        let mut l = self.clone();
        l.spacing = spacing;
        l
    }

    /// Set the flex mode: "start" | "end" | "center" | "space_between" | "space_around".
    pub fn flex_mode(&self, mode: &str) -> Layout {
        let mut l = self.clone();
        l.flex = mode.to_string();
        l
    }

    /// Split `area` according to the configured constraints.
    ///
    /// Returns a list of `Rect` objects, one per constraint.
    pub fn split(&self, area: &Rect) -> PyResult<Vec<Rect>> {
        use ratatui::layout::{Flex};

        if self.constraints.is_empty() {
            return Err(layout_err_to_py("No constraints set on Layout"));
        }

        let rust_constraints: Vec<RConstraint> = self.constraints
            .iter()
            .map(|c| c.inner)
            .collect();

        let flex = match self.flex.as_str() {
            "start"        => Flex::Start,
            "end"          => Flex::End,
            "center"       => Flex::Center,
            "space_between"=> Flex::SpaceBetween,
            "space_around" => Flex::SpaceAround,
            _              => Flex::Start,
        };

        let layout = RLayout::default()
            .direction(self.direction.to_ratatui())
            .constraints(rust_constraints)
            .margin(self.margin)
            .spacing(self.spacing)
            .flex(flex);

        let rects = layout.split(area.inner);

        Ok(rects.iter().map(|r| Rect { inner: *r }).collect())
    }

    fn __repr__(&self) -> String {
        format!("Layout(direction={:?}, constraints={}, margin={})",
            self.direction, self.constraints.len(), self.margin)
    }
}

// ─── Module registration ───────────────────────────────────────────────────────

pub fn register_layout(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Rect>()?;
    m.add_class::<Constraint>()?;
    m.add_class::<Direction>()?;
    m.add_class::<Alignment>()?;
    m.add_class::<Layout>()?;
    Ok(())
}
