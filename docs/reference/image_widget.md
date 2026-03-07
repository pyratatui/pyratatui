# Image Widget

The `ImageWidget` displays images in the terminal using
[ratatui-image](https://crates.io/crates/ratatui-image).

Supports unicode half-blocks (works everywhere), plus Sixel, Kitty, and iTerm2
graphics protocols on supported terminals.

## Quick Start

```python
from pyratatui import ImagePicker, ImageWidget, Terminal

picker = ImagePicker.halfblocks()
state  = picker.load("photo.png")
widget = ImageWidget()

with Terminal() as term:
    def ui(frame):
        frame.render_stateful_image(widget, frame.area, state)
    term.draw(ui)
```

## API

### `ImagePicker`

| Method | Description |
|--------|-------------|
| `ImagePicker.halfblocks()` | Use unicode half-blocks (any terminal) |
| `ImagePicker.with_font_size(w, h)` | Specify cell pixel size explicitly |
| `.load(path)` | Load image and return `ImageState` |

### `ImageState`

Mutable render state holding the encoded protocol data.

| Property | Description |
|----------|-------------|
| `.path` | Source file path |

### `ImageWidget()`

Stateless widget that adapts to its render area.

## Rendering

```python
frame.render_stateful_image(widget, area, state)
```

See `examples/30_image_view.py`.
