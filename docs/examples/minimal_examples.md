# Minimal Examples

Ten standalone, copy-paste-ready demos — each under 40 lines, covering every major widget and feature.

---

## 1. Hello World

The absolute minimum: one `Paragraph` in a `Block`, quit on `q`.

```python
# examples/01_hello_world.py
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

---

## 2. Three-Panel Layout

Vertical split: header / body / footer.

```python
# examples/02_layout.py
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Paragraph, Block, Style, Color,
)

with Terminal() as term:
    while True:
        def ui(frame):
            chunks = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([
                    Constraint.length(3),
                    Constraint.fill(1),
                    Constraint.length(1),
                ])
                .split(frame.area)
            )
            frame.render_widget(
                Paragraph.from_string("My App").centered()
                    .block(Block().bordered()),
                chunks[0],
            )
            frame.render_widget(
                Paragraph.from_string("Main content area\n\nPress q to quit.")
                    .block(Block().bordered().title("Body")),
                chunks[1],
            )
            frame.render_widget(
                Paragraph.from_string(" q: Quit")
                    .style(Style().fg(Color.dark_gray())),
                chunks[2],
            )

        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

---

## 3. Styled Text

`Span` → `Line` → `Text` hierarchy with per-span colors and alignment.

```python
# examples/03_styled_text.py
from pyratatui import (
    Terminal, Paragraph, Text, Line, Span,
    Block, Style, Color,
)

TEXT = Text([
    Line.from_string("Text Styling Demo").centered(),
    Line.from_string(""),
    Line([
        Span("Foreground: "),
        Span("red",   Style().fg(Color.red())),
        Span(", "),
        Span("green", Style().fg(Color.green())),
        Span(", "),
        Span("cyan",  Style().fg(Color.cyan())),
    ]),
    Line([
        Span("Modifiers: "),
        Span("bold",      Style().bold()),
        Span(", "),
        Span("italic",    Style().italic()),
        Span(", "),
        Span("underline", Style().underlined()),
        Span(", "),
        Span("dim",       Style().dim()),
    ]),
    Line([Span("RGB color: "),
          Span("salmon",  Style().fg(Color.rgb(250, 128, 114))),
          Span(", "),
          Span("teal",    Style().fg(Color.rgb(  0, 180, 180)))]),
    Line.from_string(""),
    Line.from_string("Press q to quit").right_aligned(),
])

with Terminal() as term:
    while True:
        def ui(frame):
            frame.render_widget(
                Paragraph(TEXT).block(Block().bordered().title("Styles")),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

---

## 4. List Navigation

Scrollable list with keyboard navigation.

```python
# examples/04_list_navigation.py
from pyratatui import (
    Terminal, List, ListItem, ListState,
    Block, Style, Color, BorderType,
)

ITEMS = [f"Item {i+1:02d}" for i in range(20)]
items = [ListItem(t) for t in ITEMS]
state = ListState()
state.select(0)

with Terminal() as term:
    while True:
        def ui(frame, _state=state):
            frame.render_stateful_list(
                List(items)
                    .block(Block().bordered()
                           .title(f" List ({_state.selected+1}/{len(items)}) ")
                           .border_type(BorderType.Rounded))
                    .highlight_style(Style().fg(Color.black()).bg(Color.cyan()))
                    .highlight_symbol("▶ "),
                frame.area,
                _state,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q":
                break
            elif ev.code == "Down":
                state.select_next()
            elif ev.code == "Up":
                state.select_previous()
            elif ev.code == "Home":
                state.select_first()
            elif ev.code == "End":
                state.select_last()
```

---

## 5. Progress Bar

Animated `Gauge` that fills up automatically.

```python
# examples/05_progress_bar.py
import time
from pyratatui import Terminal, Gauge, Block, Style, Color

progress = 0.0
last = time.monotonic()

with Terminal() as term:
    term.hide_cursor()
    while True:
        now = time.monotonic()
        progress = min(1.0, progress + (now - last) * 0.2)  # 20% per second
        last = now

        def ui(frame, p=progress):
            color = (Color.green() if p < 0.5
                     else Color.yellow() if p < 0.8
                     else Color.red())
            label = "Done! ✓" if p >= 1.0 else f"{p*100:.1f}%"
            frame.render_widget(
                Gauge()
                    .ratio(p)
                    .label(label)
                    .style(Style().fg(color))
                    .gauge_style(Style().fg(Color.dark_gray()))
                    .use_unicode(True)
                    .block(Block().bordered().title("Download")),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=33)  # ~30 fps
        if ev and ev.code == "q":
            break
    term.show_cursor()
```

---

## 6. Dynamic Table

Keyboard-navigable table with per-cell styling.

```python
# examples/06_table_dynamic.py
from pyratatui import (
    Terminal, Table, Row, Cell, TableState,
    Constraint, Block, Style, Color, Paragraph,
)

DATA = [
    ("nginx",    32, "Running"),
    ("postgres", 71, "Running"),
    ("redis",    5,  "Degraded"),
    ("kafka",    0,  "Stopped"),
]

def make_rows():
    color = lambda c: Color.green() if c < 50 else Color.yellow() if c < 80 else Color.red()
    st_color = {"Running": Color.green(), "Degraded": Color.yellow(), "Stopped": Color.red()}
    return [Row([Cell(n), Cell(f"{c}%").style(Style().fg(color(c))),
                 Cell(s).style(Style().fg(st_color[s]))])
            for n, c, s in DATA]

state = TableState()
state.select(0)

with Terminal() as term:
    while True:
        def ui(frame, _state=state):
            chunks = (Layout().direction(Direction.Vertical)
                .constraints([Constraint.fill(1), Constraint.length(1)])
                .split(frame.area))
            frame.render_stateful_table(
                Table(make_rows(),
                      widths=[Constraint.fill(1), Constraint.length(8), Constraint.length(10)],
                      header=Row.from_strings(["Service","CPU","Status"])
                              .style(Style().bold().fg(Color.white())))
                    .block(Block().bordered().title("Services"))
                    .highlight_style(Style().fg(Color.cyan()).bold())
                    .highlight_symbol("▶ "),
                chunks[0], _state)
            frame.render_widget(
                Paragraph.from_string(" ↑/↓: Navigate  q: Quit")
                    .style(Style().fg(Color.dark_gray())), chunks[1])
        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q": break
            elif ev.code == "Down": state.select_next()
            elif ev.code == "Up": state.select_previous()

from pyratatui import Layout  # ensure import for the example above
```

---

## 7. Bar Chart

`BarChart` with `BarGroup` and styled bars.

```python
# examples/07_barchart.py
from pyratatui import (
    Terminal, BarChart, BarGroup, Bar,
    Block, Style, Color,
)

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
VALUES = [42, 68, 35, 91, 57, 74]

bars = [
    Bar(v, m).style(Style().fg(Color.cyan() if v < 60 else Color.yellow()))
    for v, m in zip(VALUES, MONTHS)
]

with Terminal() as term:
    while True:
        def ui(frame):
            frame.render_widget(
                BarChart()
                    .data(BarGroup(bars, label="CPU %"))
                    .bar_width(5)
                    .bar_gap(1)
                    .max(100)
                    .value_style(Style().fg(Color.white()).bold())
                    .label_style(Style().fg(Color.dark_gray()))
                    .block(Block().bordered().title("Monthly CPU Usage")),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

---

## 8. Sparkline History

Sparkline showing a live rolling window of values.

```python
# examples/08_sparkline.py
import math, time
from pyratatui import Terminal, Sparkline, Block, Style, Color

history = [0] * 40

with Terminal() as term:
    start = time.monotonic()
    while True:
        t = time.monotonic() - start
        new_val = int(50 + 45 * math.sin(t * 1.5))
        history.append(new_val)
        history = history[-40:]

        def ui(frame, h=list(history)):
            frame.render_widget(
                Sparkline()
                    .data(h)
                    .max(100)
                    .style(Style().fg(Color.green()))
                    .block(Block().bordered().title(
                        f" CPU History  current={h[-1]}%")),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

---

## 9. Tabs Navigation

Multi-tab UI with keyboard switching.

```python
# examples/09_tabs.py
from pyratatui import (
    Terminal, Tabs, Layout, Constraint, Direction,
    Paragraph, Block, Style, Color,
)

TABS = ["Overview", "Services", "Logs"]
current = 0

CONTENT = [
    "Overview tab: system metrics and health indicators.",
    "Services tab: list of all running microservices.",
    "Logs tab: recent log entries from all services.",
]

with Terminal() as term:
    while True:
        tab = current
        def ui(frame, _tab=tab):
            chunks = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([Constraint.length(3), Constraint.fill(1)])
                .split(frame.area)
            )
            frame.render_widget(
                Tabs(TABS)
                    .select(_tab)
                    .block(Block().bordered())
                    .highlight_style(Style().fg(Color.cyan()).bold())
                    .style(Style().fg(Color.dark_gray())),
                chunks[0],
            )
            frame.render_widget(
                Paragraph.from_string(CONTENT[_tab])
                    .block(Block().bordered().title(TABS[_tab])),
                chunks[1],
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev:
            if ev.code == "q":
                break
            elif ev.code == "Tab":
                current = (current + 1) % len(TABS)
            elif ev.code == "BackTab":
                current = (current - 1) % len(TABS)
```

---

## 10. TachyonFX Fade Demo

Fade-in animation on startup, then continuous fade cycle.

```python
# examples/10_fade_effect.py
import time
from pyratatui import (
    Terminal, Paragraph, Block, Style, Color,
    Effect, EffectManager, Interpolation,
)

mgr  = EffectManager()
mgr.add(Effect.fade_from_fg(Color.black(), 1500, Interpolation.SineOut))
last = time.monotonic()

with Terminal() as term:
    term.hide_cursor()
    while True:
        now = time.monotonic()
        ms  = int((now - last) * 1000)
        last = now

        def ui(frame, _mgr=mgr, _ms=ms):
            area = frame.area
            # 1. Render widget
            frame.render_widget(
                Paragraph.from_string(
                    "TachyonFX Fade Demo\n\n"
                    "Text fades in on startup.\n\n"
                    "Press q to quit."
                ).block(Block().bordered().title(" Effects "))
                 .style(Style().fg(Color.white())),
                area,
            )
            # 2. Apply effect (after rendering)
            frame.apply_effect_manager(_mgr, _ms, area)

        term.draw(ui)
        ev = term.poll_event(timeout_ms=16)
        if ev and ev.code == "q":
            break
    term.show_cursor()
```
