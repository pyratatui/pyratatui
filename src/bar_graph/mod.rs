// src/bar_graph/mod.rs — Python bindings for tui-bar-graph 0.3.x

use pyo3::prelude::*;
use tui_bar_graph::{BarGraph as RBarGraph, BarStyle as RBarStyle, ColorMode as RColorMode};

// ─── BarGraphStyle ────────────────────────────────────────────────────────────

/// Bar rendering style.
///
/// Use as class attributes: ``BarGraphStyle.Braille``, ``BarGraphStyle.HalfBlock``, etc.
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Copy, Debug)]
pub struct BarGraphStyle {
    pub(crate) inner: RBarStyle,
}

#[pymethods]
impl BarGraphStyle {
    #[classattr]
    #[allow(non_snake_case)]
    pub fn Braille() -> Self {
        Self {
            inner: RBarStyle::Braille,
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    pub fn Solid() -> Self {
        Self {
            inner: RBarStyle::Solid,
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    pub fn Quadrant() -> Self {
        Self {
            inner: RBarStyle::Quadrant,
        }
    }

    #[classattr]
    #[allow(non_snake_case)]
    pub fn Octant() -> Self {
        Self {
            inner: RBarStyle::Octant,
        }
    }

    fn __repr__(&self) -> String {
        format!("BarGraphStyle({:?})", self.inner)
    }
}

// ─── BarColorMode ─────────────────────────────────────────────────────────────

/// Colour-mode for bar graphs.
///
/// Use as class attributes: ``BarColorMode.VerticalGradient``, etc.
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Copy, Debug)]
pub struct BarColorMode {
    pub(crate) inner: RColorMode,
}

#[pymethods]
impl BarColorMode {
    #[classattr]
    #[allow(non_snake_case)]
    pub fn VerticalGradient() -> Self {
        Self {
            inner: RColorMode::VerticalGradient,
        }
    }

    fn __repr__(&self) -> String {
        format!("BarColorMode({:?})", self.inner)
    }
}

// ─── BarGraph ─────────────────────────────────────────────────────────────────

/// A bold, colourful bar-graph widget.
///
/// ```python
/// from pyratatui import BarGraph, BarGraphStyle, BarColorMode
/// graph = (
///     BarGraph([0.1, 0.5, 0.3, 0.9, 0.7])
///         .bar_style(BarGraphStyle.Braille)
///         .color_mode(BarColorMode.VerticalGradient)
///         .gradient("turbo")
/// )
/// frame.render_widget(graph, area)
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone)]
pub struct BarGraph {
    data: Vec<f64>,
    bar_style: Option<RBarStyle>,
    color_mode: Option<RColorMode>,
    gradient: String,
}

impl BarGraph {
    pub(crate) fn to_ratatui(&self) -> RBarGraph<'_> {
        let grad = gradient_by_name(&self.gradient);
        let mut g = RBarGraph::new(self.data.clone()).with_gradient(grad);
        if let Some(bs) = self.bar_style {
            g = g.with_bar_style(bs);
        }
        if let Some(cm) = self.color_mode {
            g = g.with_color_mode(cm);
        }
        g
    }
}

fn gradient_by_name(name: &str) -> Box<dyn colorgrad::Gradient> {
    match name.to_lowercase().as_str() {
        "sinebow" => Box::new(colorgrad::preset::sinebow()),
        "plasma" => Box::new(colorgrad::preset::plasma()),
        "inferno" => Box::new(colorgrad::preset::inferno()),
        "magma" => Box::new(colorgrad::preset::magma()),
        "viridis" => Box::new(colorgrad::preset::viridis()),
        "rainbow" => Box::new(colorgrad::preset::rainbow()),
        _ => Box::new(colorgrad::preset::turbo()),
    }
}

#[pymethods]
impl BarGraph {
    #[new]
    pub fn new(data: Vec<f64>) -> Self {
        Self {
            data,
            bar_style: None,
            color_mode: None,
            gradient: "turbo".into(),
        }
    }

    /// Number of data points.
    #[getter]
    pub fn len(&self) -> usize {
        self.data.len()
    }

    pub fn bar_style(&self, style: &BarGraphStyle) -> Self {
        let mut s = self.clone();
        s.bar_style = Some(style.inner);
        s
    }

    pub fn color_mode(&self, mode: &BarColorMode) -> Self {
        let mut s = self.clone();
        s.color_mode = Some(mode.inner);
        s
    }

    /// Gradient name: "turbo", "plasma", "inferno", "magma", "viridis",
    /// "rainbow", "sinebow".
    pub fn gradient(&self, name: &str) -> Self {
        let mut s = self.clone();
        s.gradient = name.to_string();
        s
    }

    pub fn data(&self, values: Vec<f64>) -> Self {
        let mut s = self.clone();
        s.data = values;
        s
    }

    fn __repr__(&self) -> String {
        format!("BarGraph(len={})", self.data.len())
    }
}

// ─── Registration ─────────────────────────────────────────────────────────────

pub fn register_bar_graph(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BarGraph>()?;
    m.add_class::<BarGraphStyle>()?;
    m.add_class::<BarColorMode>()?;
    Ok(())
}
