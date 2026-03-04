# Quickstart

This tutorial walks you from zero to a working terminal UI in about 5 minutes.

---

## Step 1 — Install

```bash
pip install pyratatui
```

---

## Step 2 — Hello World

Create `hello.py`:

```python
from pyratatui import Terminal, Paragraph, Block, Style, Color

with Terminal() as term:
    while True:
        def ui(frame):
            frame.render_widget(
                Paragraph.from_string("Hello, pyratatui! 🐀  Press q to quit.")
                    .block(Block().bordered().title("Hello World"))
                    .style(Style().fg(Color.cyan())),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

Run it:

```bash
python hello.py
```

You should see:

```
┌ Hello World ────────────────────────────────────────────┐
│ Hello, pyratatui! 🐀  Press q to quit.                  │
└─────────────────────────────────────────────────────────┘
```

---

## What Just Happened

**`Terminal`** is the main entry point. Used as a context manager, it:

1. Saves the current terminal state
2. Enters alternate screen mode (your shell is hidden)
3. Enables raw input (no buffering — key presses arrive immediately)
4. Restores everything on exit, even after exceptions

**`term.draw(ui)`** accepts a callable `ui(frame)` and calls it with a fresh `Frame`. Anything you render inside that function appears on screen.

**`term.poll_event(timeout_ms=100)`** waits up to 100 ms for a key press and returns a `KeyEvent` or `None`.

**`Paragraph.from_string(...)`** creates a text widget. Every widget builder method returns a new instance (immutable builder pattern), so you can chain calls freely.

---

## Step 3 — Add a Layout

Real apps split the screen into regions. `Layout` divides a `Rect` into child `Rect`s:

```python
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Paragraph, Block, Style, Color,
)

with Terminal() as term:
    while True:
        def ui(frame):
            area = frame.area

            # Split vertically: 3-row header, fill body, 1-row footer
            chunks = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([
                    Constraint.length(3),
                    Constraint.fill(1),
                    Constraint.length(1),
                ])
                .split(area)
            )
            header, body, footer = chunks

            frame.render_widget(
                Paragraph.from_string("My Application")
                    .centered()
                    .block(Block().bordered()),
                header,
            )
            frame.render_widget(
                Paragraph.from_string("Main content area")
                    .block(Block().bordered().title("Content")),
                body,
            )
            frame.render_widget(
                Paragraph.from_string("q: quit")
                    .style(Style().fg(Color.dark_gray())),
                footer,
            )

        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

```
┌────────────────────────────────────────┐
│           My Application               │
├ Content ───────────────────────────────┤
│ Main content area                      │
│                                        │
│                                        │
└────────────────────────────────────────┘
 q: quit
```

---

## Step 4 — Handle More Keys

`KeyEvent` has three properties alongside `code`:

```python
ev = term.poll_event(timeout_ms=100)
if ev:
    print(ev.code)    # "a", "Enter", "Up", "F1", etc.
    print(ev.ctrl)    # True if Ctrl was held
    print(ev.alt)     # True if Alt was held
    print(ev.shift)   # True if Shift was held
```

Common key codes:

| Key pressed | `ev.code` |
|---|---|
| Letter/number | `"a"`, `"Z"`, `"5"` |
| Enter | `"Enter"` |
| Escape | `"Esc"` |
| Backspace | `"Backspace"` |
| Arrow keys | `"Up"`, `"Down"`, `"Left"`, `"Right"` |
| Tab / Shift-Tab | `"Tab"`, `"BackTab"` |
| Function keys | `"F1"` … `"F12"` |
| Ctrl+C | `ev.code == "c" and ev.ctrl` |

---

## Step 5 — Add State

Terminal UIs are stateful. Store state in a plain Python dict (or dataclass) outside the render function, capture it into the closure per frame:

```python
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Paragraph, Block, Style, Color, Text, Line, Span,
)

state = {"count": 0, "color_idx": 0}
COLORS = [Color.cyan(), Color.green(), Color.yellow(), Color.magenta()]

with Terminal() as term:
    while True:
        # Snapshot state for this frame (avoids closure mutation bugs)
        count = state["count"]
        color = COLORS[state["color_idx"] % len(COLORS)]

        def ui(frame, _count=count, _color=color):
            area = frame.area
            chunks = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([Constraint.fill(1), Constraint.length(1)])
                .split(area)
            )

            frame.render_widget(
                Paragraph(
                    Text([
                        Line([
                            Span("Counter: ", Style().bold()),
                            Span(str(_count), Style().fg(_color).bold()),
                        ]),
                        Line.from_string(""),
                        Line.from_string("Space: increment  c: change color  q: quit"),
                    ])
                )
                .block(Block().bordered().title("Counter Demo"))
                .centered(),
                chunks[0],
            )
            frame.render_widget(
                Paragraph.from_string(f"count={_count}")
                    .style(Style().fg(Color.dark_gray())),
                chunks[1],
            )

        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q":
                break
            elif ev.code == " ":
                state["count"] += 1
            elif ev.code == "c":
                state["color_idx"] += 1
```

!!! tip "Closure Capture Pattern"
    Always capture current state into default arguments (`_count=count`) rather than referencing outer variables directly. Python closures capture variables by reference, so a variable mutated after the function is defined will show the *new* value when the closure runs — which causes flickering or logic bugs in fast render loops.

---

## Step 6 — Styled Text

The text hierarchy is `Span` → `Line` → `Text`:

```python
from pyratatui import Text, Line, Span, Style, Color, Modifier

# A single styled span
s = Span("bold red", Style().fg(Color.red()).bold())

# A line of mixed spans
line = Line([
    Span("Status: ", Style().bold()),
    Span("OK", Style().fg(Color.green())),
    Span("  |  ", Style().fg(Color.dark_gray())),
    Span("99.9%", Style().fg(Color.cyan())),
])

# Multi-line text
text = Text([
    Line.from_string("Line 1 — plain"),
    line,
    Line.from_string("Line 3").right_aligned(),
])
```

Pass a `Text` to `Paragraph()`:

```python
frame.render_widget(Paragraph(text).block(Block().bordered()), area)
```

---

## Next Steps

- **[Async Updates](async_updates.md)** — add live background data with `AsyncTerminal`
- **[Progress Bar Tutorial](progress_bar.md)** — animated `Gauge` and `LineGauge`
- **[TachyonFX Effects](tachyonfx_effects.md)** — fade, sweep, and dissolve animations
- **[Widgets Reference](../reference/widgets.md)** — every widget documented in full
- **[Minimal Examples](../examples/minimal_examples.md)** — 10 standalone copy-paste demos
