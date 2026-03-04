# Buffer Reference

```python
from pyratatui import Buffer, Rect
```

`Buffer` is ratatui's intermediate rendering surface — an in-memory grid of styled cells that widgets write into before the terminal backend flushes the content to screen.

**Direct buffer manipulation is rarely needed in Python.** `Frame.render_widget()` writes into the buffer automatically. The `Buffer` class is primarily useful for:

- Low-level custom rendering
- Testing widget output without a real terminal
- Advanced effect pipelines that need raw cell access

---

## Constructor

```python
Buffer(area: Rect)
```

Creates a blank buffer covering the given area. All cells are initialized to blank (space character, default style).

```python
from pyratatui import Buffer, Rect

buf = Buffer(Rect(0, 0, 80, 24))
```

---

## Properties

| Property | Type | Description |
|---|---|---|
| `area` | `Rect` | The rectangle this buffer covers |

---

## Methods

### `set_string(x, y, text, style=None)`

Write a plain string starting at cell `(x, y)`, optionally styled.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `x` | `int` | required | Column (0-based) |
| `y` | `int` | required | Row (0-based) |
| `text` | `str` | required | Text to write |
| `style` | `Style \| None` | `None` | Style to apply |

```python
buf.set_string(0, 0, "Hello!", Style().fg(Color.cyan()))
buf.set_string(10, 0, "World")  # no style
```

### `set_span(x, y, span: Span)`

Write a `Span` (text + style) at `(x, y)`.

```python
from pyratatui import Span, Style, Color

buf.set_span(0, 0, Span("Hello", Style().fg(Color.green())))
```

### `get_string(x, y, width) → str`

Read `width` cell symbols starting at `(x, y)`. Returns the raw character content (without style information).

```python
content = buf.get_string(0, 0, 5)  # "Hello"
```

### `reset()`

Clear all cells to blank (space character, default style).

### `merge(other: Buffer)`

Merge `other` into `self`. Non-empty cells in `other` overwrite corresponding cells in `self`.

---

## Usage Example

```python
from pyratatui import Buffer, Rect, Style, Color

# Create an 80×24 buffer
buf = Buffer(Rect(0, 0, 80, 24))

# Write content
buf.set_string(0, 0, "Header",    Style().fg(Color.cyan()).bold())
buf.set_string(0, 1, "Body text", Style().fg(Color.white()))

# Read back
header = buf.get_string(0, 0, 6)
assert header == "Header"

# Clear and reuse
buf.reset()
```
