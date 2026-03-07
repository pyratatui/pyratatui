# Minimal Examples

Standalone, copy-paste-ready demos — each under 50 lines, covering every major
widget and feature. All examples live in the `examples/` directory.

---

## 1. Hello World

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
                Paragraph.from_string("Main content.\n\nPress q to quit.")
                    .block(Block().bordered().title("Content"))
                    .wrap(True),
                chunks[1],
            )
            frame.render_widget(
                Paragraph.from_string("  q: Quit"),
                chunks[2],
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

---

## 3. Styled Text with Spans

```python
# examples/03_styled_text.py
from pyratatui import Block, Color, Line, Paragraph, Span, Style, Terminal, Text

with Terminal() as term:
    while True:
        def ui(frame):
            text = Text([
                Line([
                    Span("Status: ", Style().bold()),
                    Span("● Running", Style().fg(Color.green()).bold()),
                ]),
                Line([Span("CPU:  "), Span("60%", Style().fg(Color.yellow()))]),
                Line([Span("MEM:  "), Span("40%", Style().fg(Color.cyan()))]),
            ])
            frame.render_widget(
                Paragraph(text).block(Block().bordered().title(" System ")),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

---

## 4. List Navigation

```python
# examples/04_list_navigation.py
from pyratatui import Block, Color, List, ListItem, ListState, Style, Terminal

items = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
state = ListState()
state.select(0)

with Terminal() as term:
    while True:
        def ui(frame, _state=state):
            lst = (
                List([ListItem(i) for i in items])
                .block(Block().bordered().title(" List "))
                .highlight_style(Style().fg(Color.black()).bg(Color.cyan()))
                .highlight_symbol("▶ ")
            )
            frame.render_stateful_list(lst, frame.area, _state)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev:
            if ev.code == "q":    break
            elif ev.code == "Down": state.select_next()
            elif ev.code == "Up":   state.select_previous()
```

---

## 5. Progress Gauge

```python
# examples/05_progress_bar.py
import time
from pyratatui import Block, Gauge, Style, Color, Terminal

with Terminal() as term:
    for step in range(101):
        def ui(frame, s=step):
            frame.render_widget(
                Gauge()
                .block(Block().bordered().title(" Progress "))
                .ratio(s / 100)
                .label(f"{s}%")
                .gauge_style(Style().fg(Color.green())),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev and ev.code == "q":
            break
        time.sleep(0.05)
```

---

## 6. Dynamic Table

```python
# examples/06_table_dynamic.py
from pyratatui import Block, Cell, Constraint, Row, Style, Color, Table, TableState, Terminal

DATA = [
    ("web-01", "23%", "45%", "Running"),
    ("db-01",  "67%", "80%", "Running"),
    ("cache-01", "1%", "12%", "Running"),
]
state = TableState()
state.select(0)

with Terminal() as term:
    while True:
        def ui(frame, _state=state):
            header = Row([Cell(h) for h in ("Server", "CPU", "Mem", "Status")])
            rows   = [Row([Cell(c) for c in row]) for row in DATA]
            tbl = (
                Table(rows)
                .header(header.style(Style().bold()))
                .column_widths([
                    Constraint.fill(1), Constraint.length(6),
                    Constraint.length(6), Constraint.length(10),
                ])
                .block(Block().bordered().title(" Servers "))
                .highlight_style(Style().fg(Color.black()).bg(Color.cyan()))
            )
            frame.render_stateful_table(tbl, frame.area, _state)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev:
            if ev.code == "q":    break
            elif ev.code == "Down": state.select_next()
            elif ev.code == "Up":   state.select_previous()
```

---

## 7. Async Reactive

```python
# examples/07_async_reactive.py
import asyncio, random
from pyratatui import AsyncTerminal, Block, Gauge, Paragraph, Style, Color

async def main():
    cpu = 0
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=10, stop_on_quit=True):
            cpu = max(0, min(100, cpu + random.randint(-5, 10)))
            def ui(frame, c=cpu):
                frame.render_widget(
                    Gauge().block(Block().bordered().title(" CPU "))
                    .ratio(c / 100).label(f"{c}%")
                    .gauge_style(Style().fg(Color.green() if c < 70 else Color.red())),
                    frame.area,
                )
            term.draw(ui)

asyncio.run(main())
```

---

## 8. TachyonFX Fade

```python
# examples/08_effects_fade.py — see full example in examples/
```

See `examples/08_effects_fade.py` for the full TachyonFX animation demo.

---

## 9. Effects DSL

See `examples/09_effects_dsl.py` for the `compile_effect` DSL demo.

---

## 10. QR Code Widget

```python
# examples/17_qrcode.py (simplified)
from pyratatui import Block, QrCodeWidget, QrColors, Terminal

qr = QrCodeWidget("https://ratatui.rs").colors(QrColors.Inverted)

with Terminal() as term:
    while True:
        def ui(frame, _qr=qr):
            blk   = Block().bordered().title(" Scan Me ")
            inner = blk.inner(frame.area)
            frame.render_widget(blk, frame.area)
            frame.render_qrcode(_qr, inner)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=30_000)
        if ev and ev.code in ("q", "Esc"):
            break
```

---

## 25. Calendar Widget *(new in 0.2.1)*

```python
# examples/25_calendar.py (simplified)
from pyratatui import (
    CalendarDate, CalendarEventStore, Monthly,
    Block, Style, Color, Terminal,
)

store = CalendarEventStore.today_highlighted(Style().fg(Color.green()).bold())
cal   = (
    Monthly(CalendarDate.today(), store)
    .block(Block().bordered().title(" Calendar "))
    .show_month_header(Style().bold().fg(Color.cyan()))
    .show_weekdays_header(Style().italic())
    .show_surrounding(Style().dim())
)

with Terminal() as term:
    while True:
        term.draw(lambda frame: frame.render_widget(cal, frame.area))
        ev = term.poll_event(timeout_ms=200)
        if ev and ev.code == "q":
            break
```

Run the full interactive version (month/year navigation):

```bash
python examples/25_calendar.py
# ←/→: month   ↑/↓: year   t: today   q: quit
```

---

## 26. Web Counter *(new in 0.2.1)*

```python
# examples/26_web_counter.py (simplified)
from pyratatui.web import WebTerminal
from pyratatui import Paragraph, Block

counter = 0

def ui(frame):
    frame.render_widget(
        Paragraph.from_string(f"Counter: {counter}")
            .block(Block().bordered().title(" Web TUI ")),
        frame.area,
    )

with WebTerminal(cols=100, rows=30) as term:
    print(f"Open: {term.url}")
    while True:
        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "Up":   counter += 1
            if ev.code == "Down": counter -= 1
            if ev.code == "q":    break
```

Run the full version:

```bash
python examples/26_web_counter.py
# → Open: http://localhost:7700/
```

---

## All Examples

| # | File | Demonstrates |
|---|------|--------------|
| 01 | `01_hello_world.py` | Paragraph, Block, Style |
| 02 | `02_layout.py` | Layout, Constraint, Direction |
| 03 | `03_styled_text.py` | Span, Line, Text, Modifier |
| 04 | `04_list_navigation.py` | List, ListState |
| 05 | `05_progress_bar.py` | Gauge, LineGauge |
| 06 | `06_table_dynamic.py` | Table, TableState |
| 07 | `07_async_reactive.py` | AsyncTerminal, asyncio |
| 08 | `08_effects_fade.py` | EffectManager, TachyonFX |
| 09 | `09_effects_dsl.py` | compile_effect DSL |
| 10 | `10_full_app.py` | Multi-tab full app |
| 11 | `11_popup_basic.py` | Popup (stateless) |
| 12 | `12_popup_stateful.py` | PopupState (draggable) |
| 13 | `13_popup_scrollable.py` | Scrollable popup |
| 14 | `14_textarea_basic.py` | TextArea, Emacs bindings |
| 15 | `15_textarea_advanced.py` | TextArea, Vim modal |
| 16 | `16_scrollview.py` | ScrollView |
| 17 | `17_qrcode.py` | QrCodeWidget |
| 18 | `18_async_progress.py` | AsyncTerminal + progress |
| 19 | `19_effects_glitch.py` | Glitch effects |
| 20 | `20_effects_matrix.py` | Matrix rain effect |
| 21 | `21_prompt_confirm.py` | PasswordPrompt |
| 22 | `22_prompt_select.py` | Select prompt |
| 23 | `23_prompt_text.py` | TextPrompt |
| 24 | `24_dashboard.py` | Full monitoring dashboard |
| **25** | **`25_calendar.py`** | **Monthly calendar widget** |
| **26** | **`26_web_counter.py`** | **pyratatui.web browser TUI** |
