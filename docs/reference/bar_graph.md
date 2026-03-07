# Bar Graph

The `BarGraph` widget renders bold, colourful bar charts using the
[tui-bar-graph](https://crates.io/crates/tui-bar-graph) crate.

## Quick Start

```python
from pyratatui import BarGraph, BarGraphStyle, BarColorMode, Terminal, Layout, Constraint

with Terminal() as term:
    def ui(frame):
        graph = (
            BarGraph([0.2, 0.8, 0.5, 0.9, 0.3, 0.6])
            .bar_style(BarGraphStyle.Braille)
            .color_mode(BarColorMode.VerticalGradient)
            .gradient("turbo")
        )
        frame.render_widget(graph, frame.area)
    term.draw(ui)
```

## API

### `BarGraph(data)`

| Method | Description |
|--------|-------------|
| `.bar_style(style)` | Set `BarGraphStyle.Braille`, `.HalfBlock`, `.Block`, `.Quadrant`, `.Octant` |
| `.color_mode(mode)` | Set `BarColorMode.VerticalGradient`, `.HorizontalGradient`, `.Bar` |
| `.gradient(name)` | Gradient: `"turbo"`, `"plasma"`, `"inferno"`, `"magma"`, `"viridis"`, `"rainbow"`, `"sinebow"` |
| `.data(values)` | Replace data values |
| `.len` | Number of bars |

### `BarGraphStyle`

| Attribute | Description |
|-----------|-------------|
| `Braille` | High-resolution braille dots |
| `HalfBlock` | Half-block characters |
| `Block` | Full block characters |
| `Quadrant` | Quadrant-resolution |
| `Octant` | Octant-resolution |

### `BarColorMode`

| Attribute | Description |
|-----------|-------------|
| `VerticalGradient` | Gradient from bottom (low) to top (high) |
| `HorizontalGradient` | Gradient from first to last bar |
| `Bar` | Single colour per bar from gradient |

## Example

See `examples/26_bar_graph.py`.
