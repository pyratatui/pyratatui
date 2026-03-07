// src/tree_widget/mod.rs — Python bindings for tui-tree-widget 0.24

use pyo3::prelude::*;
use tui_tree_widget::{TreeItem as RTreeItem, TreeState as RTreeState};

use crate::style::Style;
use crate::widgets::Block;

// ─── PyTreeItem ───────────────────────────────────────────────────────────────

/// A node in a tree widget.
///
/// ```python
/// from pyratatui import TreeItem
/// root = TreeItem("Root", [
///     TreeItem("Child 1"),
///     TreeItem("Child 2").with_child(TreeItem("Grandchild")),
/// ])
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct TreeItem {
    pub(crate) text: String,
    pub(crate) children: Vec<TreeItem>,
}

#[pymethods]
impl TreeItem {
    #[new]
    #[pyo3(signature = (text, children=None))]
    pub fn new(text: String, children: Option<Vec<TreeItem>>) -> Self {
        Self {
            text,
            children: children.unwrap_or_default(),
        }
    }

    #[getter]
    pub fn text(&self) -> &str {
        &self.text
    }

    #[getter]
    pub fn children(&self) -> Vec<TreeItem> {
        self.children.clone()
    }

    /// Return a new `TreeItem` with the given child appended.
    pub fn with_child(&self, child: TreeItem) -> TreeItem {
        let mut s = self.clone();
        s.children.push(child);
        s
    }

    fn __repr__(&self) -> String {
        format!(
            "TreeItem({:?}, children={})",
            self.text,
            self.children.len()
        )
    }
}

/// Build ratatui TreeItems with sequential usize IDs.
pub(crate) fn build_ratatui_items(
    items: &[TreeItem],
    counter: &mut usize,
) -> Vec<RTreeItem<'static, usize>> {
    items
        .iter()
        .map(|item| {
            let id = *counter;
            *counter += 1;
            if item.children.is_empty() {
                RTreeItem::new_leaf(id, item.text.clone())
            } else {
                let children = build_ratatui_items(&item.children, counter);
                RTreeItem::new(id, item.text.clone(), children)
                    .expect("duplicate tree ID — sequential IDs should never duplicate")
            }
        })
        .collect()
}

// ─── Tree widget ─────────────────────────────────────────────────────────────

/// Tree-view widget.
///
/// ```python
/// from pyratatui import Tree, TreeItem, TreeState
/// items = [TreeItem("Root", [TreeItem("Child")])]
/// tree  = Tree(items).block(Block().bordered().title(" Files "))
/// state = TreeState()
/// frame.render_stateful_tree(tree, area, state)
/// ```
#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone)]
pub struct Tree {
    pub(crate) items: Vec<TreeItem>,
    pub(crate) block: Option<Block>,
    pub(crate) highlight_style: Option<Style>,
    pub(crate) highlight_symbol: Option<String>,
}

#[pymethods]
impl Tree {
    #[new]
    pub fn new(items: Vec<TreeItem>) -> Self {
        Self {
            items,
            block: None,
            highlight_style: None,
            highlight_symbol: None,
        }
    }

    /// Number of top-level items.
    #[getter]
    pub fn len(&self) -> usize {
        self.items.len()
    }

    pub fn block(&self, block: Block) -> Self {
        let mut s = self.clone();
        s.block = Some(block);
        s
    }

    pub fn highlight_style(&self, style: Style) -> Self {
        let mut s = self.clone();
        s.highlight_style = Some(style);
        s
    }

    pub fn highlight_symbol(&self, sym: String) -> Self {
        let mut s = self.clone();
        s.highlight_symbol = Some(sym);
        s
    }

    fn __repr__(&self) -> String {
        format!("Tree(items={})", self.items.len())
    }
}

// ─── TreeState ────────────────────────────────────────────────────────────────

/// Mutable navigation state for a `Tree` widget.
///
/// ```python
/// state = TreeState()
/// state.select([0])
/// state.open([0])
/// state.key_down()
/// ```
#[pyclass(module = "pyratatui", unsendable)]
pub struct TreeState {
    pub(crate) inner: RTreeState<usize>,
    /// Items cached for key navigation.
    pub(crate) items: Vec<TreeItem>,
}

#[pymethods]
impl TreeState {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: RTreeState::default(),
            items: Vec::new(),
        }
    }

    /// Update the items used for keyboard navigation.
    pub fn set_items(&mut self, items: Vec<TreeItem>) {
        self.items = items;
    }

    /// Currently-selected identifier path, or ``None`` if nothing is selected.
    #[getter]
    pub fn selected(&self) -> Option<Vec<usize>> {
        let sel = self.inner.selected();
        if sel.is_empty() {
            None
        } else {
            Some(sel.to_vec())
        }
    }

    /// Select a node by its identifier path.  Pass an empty list to clear.
    pub fn select(&mut self, path: Vec<usize>) {
        self.inner.select(path);
    }

    /// Open (expand) a node; returns ``True`` if state changed.
    pub fn open(&mut self, path: Vec<usize>) -> bool {
        self.inner.open(path)
    }

    /// Close (collapse) a node; returns ``True`` if state changed.
    pub fn close(&mut self, path: Vec<usize>) -> bool {
        self.inner.close(&path)
    }

    /// Toggle a node's open/close state.
    pub fn toggle(&mut self, path: Vec<usize>) -> bool {
        self.inner.toggle(path)
    }

    /// Toggle the currently-selected node's open/close state.
    pub fn toggle_selected(&mut self) -> bool {
        self.inner.toggle_selected()
    }

    /// Move up; returns ``True`` if selection changed.
    pub fn key_up(&mut self) -> bool {
        self.inner.key_up()
    }

    /// Move down; returns ``True`` if selection changed.
    pub fn key_down(&mut self) -> bool {
        self.inner.key_down()
    }

    /// Collapse or move to parent; returns ``True`` if state changed.
    pub fn key_left(&mut self) -> bool {
        self.inner.key_left()
    }

    /// Expand; returns ``True`` if state changed.
    pub fn key_right(&mut self) -> bool {
        self.inner.key_right()
    }

    fn __repr__(&self) -> String {
        format!("TreeState(selected={:?})", self.inner.selected())
    }
}

impl Default for TreeState {
    fn default() -> Self {
        Self::new()
    }
}

// ─── Registration ─────────────────────────────────────────────────────────────

pub fn register_tree_widget(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<TreeItem>()?;
    m.add_class::<Tree>()?;
    m.add_class::<TreeState>()?;
    Ok(())
}
