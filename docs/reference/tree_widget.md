# Tree Widget

The `Tree` widget renders interactive collapsible tree views using
[tui-tree-widget](https://crates.io/crates/tui-tree-widget).

## Quick Start

```python
from pyratatui import Tree, TreeItem, TreeState, Block

items = [
    TreeItem("Documents", [
        TreeItem("report.pdf"),
        TreeItem("notes.md"),
    ]),
    TreeItem("Downloads"),
]

tree  = Tree(items).block(Block().bordered().title(" Files "))
state = TreeState()

# In render loop:
# frame.render_stateful_tree(tree, area, state)
```

## Keyboard Navigation

```python
ev = term.poll_event(timeout_ms=100)
if ev:
    if ev.code == "Up":    state.key_up()
    if ev.code == "Down":  state.key_down()
    if ev.code == "Left":  state.key_left()
    if ev.code == "Right": state.key_right()
```

## API

### `TreeItem(text, children=None)`

| Method | Description |
|--------|-------------|
| `.text` | Node text |
| `.children` | Child items |
| `.with_child(child)` | Return new item with child appended |

### `Tree(items)`

| Method | Description |
|--------|-------------|
| `.block(block)` | Wrap in a border block |
| `.highlight_style(style)` | Style for selected item |
| `.highlight_symbol(sym)` | Prefix for selected item |
| `.len` | Number of top-level items |

### `TreeState()`

| Method | Description |
|--------|-------------|
| `.selected` | Current selection path or `None` |
| `.select(path)` | Select node by ID path |
| `.open(path)` / `.close(path)` | Expand / collapse |
| `.toggle(path)` | Toggle open/close |
| `.key_up()` / `.key_down()` | Navigate |
| `.key_left()` / `.key_right()` | Collapse / expand |

## Rendering

```python
frame.render_stateful_tree(tree, area, state)
```

See `examples/27_tree_widget.py`.
