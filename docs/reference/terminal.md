# Terminal Reference

## Terminal

The main driver class. Opens the terminal, enables raw mode, alternate screen.

```python
from pyratatui import Terminal

# Sync context manager
with Terminal() as term:
    term.draw(lambda frame: ...)
    ev = term.poll_event(timeout_ms=100)
    term.clear()
    term.hide_cursor()
    term.show_cursor()
    area = term.area()
```

### Methods

| Method | Description |
|--------|-------------|
| `draw(fn)` | Call `fn(frame)` and flush the frame to the terminal |
| `poll_event(timeout_ms=0)` | Poll for a `KeyEvent`. Returns `None` if no event. |
| `area()` | Returns current terminal `Rect` |
| `clear()` | Force full redraw next frame |
| `hide_cursor()` | Hide the cursor |
| `show_cursor()` | Show the cursor |
| `restore()` | Restore terminal (called automatically by `__exit__`) |

## Frame

Passed into your draw callback. Use it to render widgets.

```python
def ui(frame):
    area = frame.area           # Rect
    frame.render_widget(widget, area)
    frame.render_stateful_list(lst, area, state)
    frame.render_stateful_table(tbl, area, state)
    frame.render_stateful_scrollbar(sb, area, state)
```

## KeyEvent

Returned by `term.poll_event()`.

```python
ev = term.poll_event(timeout_ms=100)
if ev:
    ev.code    # str: "a", "Enter", "Esc", "Up", "Down", "F1", ...
    ev.ctrl    # bool
    ev.alt     # bool
    ev.shift   # bool
```

## AsyncTerminal

Async context manager for asyncio applications.

```python
from pyratatui import AsyncTerminal

async with AsyncTerminal() as term:
    async for ev in term.events(fps=30):
        term.draw(ui)
```

### Events generator

```python
async for ev in term.events(fps=30, stop_on_quit=True):
    # ev: Optional[KeyEvent] — None on timer ticks, KeyEvent on key press
    term.draw(ui)
```

## run_app / run_app_async

```python
from pyratatui import run_app, run_app_async

# Sync
run_app(ui_fn, fps=30, on_key=lambda ev: ev.code == "q")

# Async
await run_app_async(ui_fn, fps=30)
```
