# Popups

The `pyratatui` popup module integrates the
[`tui-popup`](https://crates.io/crates/tui-popup) crate, providing a
ready-made centered floating popup widget with optional drag support.

---

## Overview

| Class | Purpose |
|---|---|
| `Popup` | The popup widget (stateless or stateful rendering) |
| `PopupState` | Stores position for moveable/draggable popups |
| `KnownSizeWrapper` | Wraps scrollable content with a fixed display size |

---

## `Popup`

A centered popup that overlays the rest of the UI.  Auto-sizes to content or
to the fixed size provided by a `KnownSizeWrapper`.

```python
from pyratatui import Popup, Style, Color

popup = (
    Popup("Press any key to exit.")
    .title(" Demo Popup ")
    .style(Style().fg(Color.white()).bg(Color.blue()))
)

# Stateless rendering (always centered, no state needed):
frame.render_popup(popup, frame.area)
```

### Constructor

```python
Popup(content: str | KnownSizeWrapper) -> Popup
```

- **`content`** — Either a plain string (multi-line supported) or a
  `KnownSizeWrapper` for scrollable content.

### Builder Methods

```python
popup.title(title: str) -> Popup      # Set the popup border title
popup.style(style: Style) -> Popup    # Set overall style (fg/bg colors, etc.)
```

Both methods return a **new** `Popup` instance (immutable builder pattern).

---

## `PopupState`

Stores the current screen position of a popup, enabling keyboard or
mouse-driven movement.

```python
from pyratatui import Popup, PopupState

state = PopupState()
popup = Popup("Hello!").title(" Draggable ")

def ui(frame):
    frame.render_stateful_popup(popup, frame.area, state)

# Move with keyboard:
state.move_up(1)
state.move_down(1)
state.move_left(1)
state.move_right(1)

# Move to absolute position:
state.move_to(col=10, row=5)

# Reset to center:
state.reset()
```

### Mouse Drag

Pass crossterm mouse event coordinates to enable drag-to-move behavior.
Dragging only activates when the mouse-down event lands on the **title bar row**:

```python
# Inside your event loop:
if ev.code == "MouseDown":
    state.mouse_down(ev.col, ev.row)
elif ev.code == "MouseUp":
    state.mouse_up(ev.col, ev.row)
elif ev.code == "MouseDrag":
    state.mouse_drag(ev.col, ev.row)
```

---

## `KnownSizeWrapper`

Wraps a list of text lines and provides a fixed display size, enabling
scrollable popup content.

```python
from pyratatui import KnownSizeWrapper, Popup

lines = [f"Line {i:03d}: some content here" for i in range(50)]
wrapper = KnownSizeWrapper(lines, width=50, height=10, scroll=0)

popup = Popup(wrapper).title(" Scrollable Popup ")
frame.render_popup(popup, frame.area)
```

### Constructor

```python
KnownSizeWrapper(
    lines: list[str],
    width: int,
    height: int,
    scroll: int = 0,
) -> KnownSizeWrapper
```

### Scroll Methods

```python
wrapper.scroll_down(n: int) -> None   # Scroll down n lines (clamped)
wrapper.scroll_up(n: int) -> None     # Scroll up n lines (clamped)
wrapper.scroll                        # Current scroll offset (property)
wrapper.with_scroll(scroll: int) -> KnownSizeWrapper  # Builder
```

---

## Frame Render Methods

Two new methods are added to `Frame`:

```python
frame.render_popup(popup: Popup, area: Rect) -> None
```
Render a popup **stateless** — always centered in `area`.

```python
frame.render_stateful_popup(popup: Popup, area: Rect, state: PopupState) -> None
```
Render a popup **stateful** — position is tracked in `state`, enabling
keyboard/mouse movement.

---

## Complete Example

```python
import time
from pyratatui import (
    Color, KnownSizeWrapper, Paragraph, Popup, PopupState,
    Style, Terminal,
)

lines = [f"  {i:03d}. Item number {i}" for i in range(1, 31)]
wrapper = KnownSizeWrapper(lines, width=40, height=8)
state = PopupState()
bg = Paragraph.from_string("background").style(Style().fg(Color.dark_gray()))

popup = (
    Popup(wrapper)
    .title(" Scrollable & Draggable ")
    .style(Style().fg(Color.white()).bg(Color.dark_gray()))
)

with Terminal() as term:
    while True:
        def ui(frame, _p=popup, _s=state):
            frame.render_widget(bg, frame.area)
            frame.render_stateful_popup(_p, frame.area, _s)
        term.draw(ui)

        ev = term.poll_event(timeout_ms=50)
        if ev is None:
            continue
        if ev.code in ("q", "Esc"):
            break
        elif ev.code == "Up":
            state.move_up(1)
        elif ev.code == "Down":
            state.move_down(1)
        elif ev.code == "Left":
            state.move_left(1)
        elif ev.code == "Right":
            state.move_right(1)
        elif ev.code == "r":
            state.reset()
```

---

## See Also

- [`tui-popup` crate](https://crates.io/crates/tui-popup)
- [`tui-popup` docs](https://docs.rs/tui-popup)
- [Example 11 — Basic Popup](../../examples/11_popup_basic.py)
- [Example 12 — Stateful Popup](../../examples/12_popup_stateful.py)
- [Example 13 — Scrollable Popup](../../examples/13_popup_scrollable.py)
