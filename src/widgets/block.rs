// src/widgets/block.rs
//! Python binding for the `Block` widget.

use pyo3::prelude::*;
use ratatui::widgets::{
    Block as RBlock,
    Borders,
    BorderType as RBorderType,
    Padding as RPadding,
};
use ratatui::layout::Alignment;

use crate::style::Style;

// ─── BorderType ───────────────────────────────────────────────────────────────

/// The visual style of a block border.
#[pyclass(module = "pyratatui", eq, eq_int)]
#[derive(Clone, Debug, PartialEq)]
pub enum BorderType {
    Plain,
    Rounded,
    Double,
    Thick,
    QuadrantInside,
    QuadrantOutside,
}

impl BorderType {
    fn to_ratatui(&self) -> RBorderType {
        match self {
            BorderType::Plain            => RBorderType::Plain,
            BorderType::Rounded          => RBorderType::Rounded,
            BorderType::Double           => RBorderType::Double,
            BorderType::Thick            => RBorderType::Thick,
            BorderType::QuadrantInside   => RBorderType::QuadrantInside,
            BorderType::QuadrantOutside  => RBorderType::QuadrantOutside,
        }
    }
}

// ─── Block ────────────────────────────────────────────────────────────────────

/// A bordered container widget.
///
/// ```python
/// from pyratatui import Block, Style, Color, BorderType
///
/// block = (Block()
///     .title("My App")
///     .bordered()
///     .border_type(BorderType.Rounded)
///     .style(Style().fg(Color.cyan())))
/// ```
#[pyclass(module = "pyratatui")]
#[derive(Clone, Debug)]
pub struct Block {
    title: Option<String>,
    title_bottom: Option<String>,
    borders: u8,   // bit flags: 1=top, 2=right, 4=bottom, 8=left
    border_type: BorderType,
    style: Option<Style>,
    title_style: Option<Style>,
    border_style: Option<Style>,
    padding_left: u16,
    padding_right: u16,
    padding_top: u16,
    padding_bottom: u16,
    title_alignment: String,
}

impl Block {
    fn borders_flags(&self) -> Borders {
        let mut b = Borders::NONE;
        if self.borders & 1 != 0 { b |= Borders::TOP; }
        if self.borders & 2 != 0 { b |= Borders::RIGHT; }
        if self.borders & 4 != 0 { b |= Borders::BOTTOM; }
        if self.borders & 8 != 0 { b |= Borders::LEFT; }
        b
    }

    pub(crate) fn to_ratatui(&self) -> RBlock<'static> {
        let mut block = RBlock::default()
            .borders(self.borders_flags())
            .border_type(self.border_type.to_ratatui())
            .padding(RPadding {
                left: self.padding_left,
                right: self.padding_right,
                top: self.padding_top,
                bottom: self.padding_bottom,
            });

        if let Some(ref t) = self.title {
            let align = match self.title_alignment.as_str() {
                "center" => Alignment::Center,
                "right"  => Alignment::Right,
                _        => Alignment::Left,
            };
            let line = if let Some(ref ts) = self.title_style {
                ratatui::text::Line::from(ratatui::text::Span::styled(t.clone(), ts.inner))
            } else {
                ratatui::text::Line::from(t.clone())
            };
            block = block.title(line).title_alignment(align);
        }
        if let Some(ref b) = self.title_bottom {
            let line = ratatui::text::Line::from(b.clone());
            block = block.title_bottom(line);
        }
        if let Some(ref s) = self.style {
            block = block.style(s.inner);
        }
        if let Some(ref s) = self.border_style {
            block = block.border_style(s.inner);
        }
        block
    }
}

#[pymethods]
impl Block {
    /// Create an empty block with no borders or title.
    #[new]
    pub fn new() -> Self {
        Self {
            title: None,
            title_bottom: None,
            borders: 0,
            border_type: BorderType::Plain,
            style: None,
            title_style: None,
            border_style: None,
            padding_left: 0,
            padding_right: 0,
            padding_top: 0,
            padding_bottom: 0,
            title_alignment: "left".into(),
        }
    }

    /// Set the top title. Returns `self` for chaining.
    pub fn title(&self, title: &str) -> Block {
        let mut b = self.clone();
        b.title = Some(title.to_string());
        b
    }

    /// Set a title at the bottom of the block.
    pub fn title_bottom(&self, title: &str) -> Block {
        let mut b = self.clone();
        b.title_bottom = Some(title.to_string());
        b
    }

    /// Enable all four borders.
    pub fn bordered(&self) -> Block {
        let mut b = self.clone();
        b.borders = 0b1111;
        b
    }

    /// Enable specific borders.
    ///
    /// Args:
    ///     top, right, bottom, left: booleans
    #[pyo3(signature = (top=true, right=true, bottom=true, left=true))]
    pub fn borders(&self, top: bool, right: bool, bottom: bool, left: bool) -> Block {
        let mut b = self.clone();
        b.borders =
            (top    as u8)       |
            ((right  as u8) << 1)|
            ((bottom as u8) << 2)|
            ((left   as u8) << 3);
        b
    }

    /// Set the border visual type.
    pub fn border_type(&self, bt: &BorderType) -> Block {
        let mut b = self.clone();
        b.border_type = bt.clone();
        b
    }

    /// Set the block background / text style.
    pub fn style(&self, style: &Style) -> Block {
        let mut b = self.clone();
        b.style = Some(style.clone());
        b
    }

    /// Style applied to the title text.
    pub fn title_style(&self, style: &Style) -> Block {
        let mut b = self.clone();
        b.title_style = Some(style.clone());
        b
    }

    /// Style applied to the border characters.
    pub fn border_style(&self, style: &Style) -> Block {
        let mut b = self.clone();
        b.border_style = Some(style.clone());
        b
    }

    /// Set inner padding.
    #[pyo3(signature = (left=0, right=0, top=0, bottom=0))]
    pub fn padding(&self, left: u16, right: u16, top: u16, bottom: u16) -> Block {
        let mut b = self.clone();
        b.padding_left = left;
        b.padding_right = right;
        b.padding_top = top;
        b.padding_bottom = bottom;
        b
    }

    /// Set the horizontal alignment of the title ("left", "center", "right").
    pub fn title_alignment(&self, alignment: &str) -> Block {
        let mut b = self.clone();
        b.title_alignment = alignment.to_string();
        b
    }

    fn __repr__(&self) -> String {
        format!("Block(title={:?}, borders=0b{:04b})", self.title, self.borders)
    }
}

pub fn register_block(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Block>()?;
    m.add_class::<BorderType>()?;
    Ok(())
}
