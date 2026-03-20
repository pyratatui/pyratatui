# Image Widget

The `ImageWidget` displays images in the terminal using
[ratatui-image](https://crates.io/crates/ratatui-image).

It supports multiple protocols, from universal Unicode half-blocks to full
pixel graphics protocols.

## Protocols

- **Halfblocks**: Unicode block elements (U+2580-U+2588).
  Works everywhere, but lowest fidelity. Great fallback.
  Reference: [Unicode Block Elements](https://www.unicode.org/versions/Unicode12.1.0/ch22.pdf).
- **Sixel**: Paletted bitmap graphics (DEC VT3xx / xterm).
  Good quality where supported.
  Reference: [xterm control sequences (Sixel)](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html).
- **Kitty**: Kitty graphics protocol (pixel-accurate, fast).
  Reference: [kitty graphics protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/).
- **iTerm2**: Inline images protocol (pixel-accurate, widely supported on macOS).
  Reference: [iTerm2 inline images](https://iterm2.com/documentation-images.html).

## Quick Start (Best Quality)

Use `from_query()` so the picker can query the terminal for the best available
protocol and the actual cell pixel size. This performs terminal I/O, so call it
after entering `Terminal()` and before you start reading events.

```python
from pyratatui import ImagePicker, ImageWidget, Terminal

with Terminal() as term:
    try:
        picker = ImagePicker.from_query()
    except RuntimeError:
        picker = ImagePicker.halfblocks()

    state  = picker.load("photo.png")
    widget = ImageWidget()

    def ui(frame):
        frame.render_stateful_image(widget, frame.area, state)

    term.draw(ui)
```

## API

### `ImagePicker`

| Method | Description |
|--------|-------------|
| `ImagePicker.halfblocks()` | Unicode half-blocks (works everywhere) |
| `ImagePicker.sixel()` | Force Sixel graphics protocol |
| `ImagePicker.kitty()` | Force Kitty graphics protocol |
| `ImagePicker.iterm2()` | Force iTerm2 inline images protocol |
| `ImagePicker.from_query()` | Query terminal for best protocol and font size |
| `ImagePicker.with_font_size(w, h)` | Specify cell pixel size explicitly |
| `.load(path)` | Load image and return `ImageState` |

### `ImageState`

Mutable render state holding the encoded protocol data.

| Property | Description |
|----------|-------------|
| `.path` | Source file path |

### `ImageWidget()`

Stateless widget that adapts to its render area. pyratatui uses a high-quality
Lanczos3 resampling filter when resizing images for rendering.

## Rendering

```python
frame.render_stateful_image(widget, area, state)
```

See `examples/30_image_view.py`.
