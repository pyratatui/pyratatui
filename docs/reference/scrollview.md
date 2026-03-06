# ScrollView

`ScrollView` provides a scrollable viewport for content larger than the terminal
screen, powered by the [`tui-scrollview`](https://crates.io/crates/tui-scrollview)
crate.

---

## Overview

| Class | Purpose |
|---|---|
| `ScrollView` | The scrollable canvas widget (created per-frame) |
| `ScrollViewState` | Persistent scroll position state |

---

## Quick Start

```python
from pyratatui import ScrollView, ScrollViewState, Terminal

lines = [f"  {i:03d} │ " + "content " * 8 for i in range(200)]
state = ScrollViewState()

with Terminal() as term:
    while True:
        sv = ScrollView.from_lines(lines, content_width=80)
        term.draw(lambda frame: frame.render_stateful_scrollview(sv, frame.area, state))
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code in ("q", "Esc"): break
            elif ev.code == "Down":     state.scroll_down(1)
            elif ev.code == "Up":       state.scroll_up(1)
            elif ev.code == "PageDown": state.scroll_down(10)
            elif ev.code == "PageUp":   state.scroll_up(10)
            elif ev.code == "Home":     state.scroll_to_top()
            elif ev.code == "End":      state.scroll_to_bottom()
```

---

## `ScrollView`

A `ScrollView` holds the content to render. Create a new instance each frame
(it is lightweight and designed to be rebuilt).

### From Lines

```python
lines = ["Line 1", "Line 2", "Line 3"]
sv = ScrollView.from_lines(lines, content_width=80)
```

### Custom Layout

```python
sv = ScrollView(content_width=80, content_height=50)

sv.add_paragraph(
    "Header text",
    x=0, y=0, width=80, height=3,
    title=" Header "    # optional: adds a border
)
sv.add_paragraph(
    "Body\nMore content",
    x=0, y=3, width=80, height=20
)
```

### Rendering

```python
frame.render_stateful_scrollview(sv, frame.area, state)
```

---

## `ScrollViewState`

```python
state = ScrollViewState()

state.scroll_down(n)     # scroll down n lines
state.scroll_up(n)       # scroll up n lines
state.scroll_right(n)    # scroll right n columns
state.scroll_left(n)     # scroll left n columns
state.scroll_to_top()    # jump to top
state.scroll_to_bottom() # jump to bottom
state.reset()            # alias for scroll_to_top

x, y = state.offset()   # current (col, row) offset
```

---

## Complete Example

See [Example 16 — ScrollView](../../examples/16_scrollview.py).

```python
lines = [f"  {i:03d}: " + "data " * 10 for i in range(200)]
state = ScrollViewState()

with Terminal() as term:
    while True:
        sv = ScrollView.from_lines(lines, content_width=100)
        term.draw(lambda frame: frame.render_stateful_scrollview(sv, frame.area, state))
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "Down":  state.scroll_down(1)
            if ev.code == "Up":    state.scroll_up(1)
            if ev.code == "q":     break
```

---

## See Also

- [`tui-scrollview` crate](https://crates.io/crates/tui-scrollview)
- [Example 16 — ScrollView](../../examples/16_scrollview.py)
