# pyratatui

<img src="https://github.com/pyratatui/pyratatui/raw/main/gallery/pyratatui.png"
     alt="PyRatatui Logo" width="96">

**Python bindings for [ratatui](https://ratatui.rs) 0.30 — high-performance terminal UIs, from Python.**

[![PyPI](https://img.shields.io/pypi/v/pyratatui?style=flat-square&logo=pypi&color=3775A9)](https://pypi.org/project/pyratatui/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![ratatui](https://img.shields.io/badge/ratatui-0.30-orange?style=flat-square)](https://ratatui.rs)
[![License](https://img.shields.io/github/license/pyratatui/pyratatui?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/pyratatui/pyratatui/ci.yml?style=flat-square)](https://github.com/pyratatui/pyratatui/actions)

---

| | | |
|---|---|---|
| ![snip1](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_1.png) | ![snip2](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_2.png) | ![snip3](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_3.png) |
| ![snip4](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_4.png) | ![snip5](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_5.png) | ![snip6](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_6.png) |
| ![snip7](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_7.png) | ![snip8](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_8.png) | ![snip9](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_9.png) |
| ![snip10](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_10.png) | ![snip11](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_11.png) | ![snip12](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_12.png) |

---

pyratatui wraps the full ratatui 0.30 widget library — including the new Calendar widget —
plus the tachyonfx animation engine and five new third-party widget integrations, all behind a
clean, typed, idiomatic Python API compiled with [PyO3](https://pyo3.rs) and [Maturin](https://github.com/PyO3/maturin).

**No runtime dependencies** — the wheel ships a self-contained native extension.

---

## What's New in 0.2.1

- **📊 BarGraph widget** — colorful gradient bar graphs via `tui-bar-graph`
- **🌲 Tree widget** — interactive hierarchical tree view via `tui-tree-widget`
- **📝 Markdown renderer** — `markdown_to_text()` converts Markdown to styled `Text` via `tui-markdown`
- **📜 Logger widget** — real-time log viewer via `tui-logger`
- **🖼 Image widget** — display images via `ratatui-image` (sixel/kitty/halfblocks)
- **📅 Calendar widget** — `Monthly`, `CalendarDate`, `CalendarEventStore`
- **🔢 30 examples** numbered `01_hello_world.py` → `30_image_view.py`

---

## Installation

```bash
pip install pyratatui
```

Pre-built wheels are available on PyPI for Linux x86_64, macOS (x86_64 + arm64),
and Windows x86_64. Python 3.10–3.13 supported.

**Build from source** (requires Rust stable + Maturin):

```bash
pip install maturin
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui
maturin develop --release
```

---

## Hello World

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

---

## Feature Overview

| Feature | Details |
|---|---|
| **Widgets** | Block, Paragraph, List, Table, Gauge, LineGauge, BarChart, Sparkline, Tabs, Scrollbar, Clear, **Monthly (calendar)** |
| **Layout** | Constraint-based splits (length, percentage, fill, min, max, ratio), flex modes, margins, spacing |
| **Styling** | 16 named + 256-indexed + RGB true-colour, 9 text modifiers, immutable builder |
| **Text** | `Span` → `Line` → `Text` hierarchy with per-span styling and alignment |
| **Async** | `AsyncTerminal` with `async for ev in term.events(fps=30)` |
| **Effects** | tachyonfx — fade, dissolve, coalesce, slide, sweep, sequence, parallel, ping-pong |
| **Prompts** | `TextPrompt`, `PasswordPrompt` with live validation |
| **Popups** | `Popup`, `PopupState` — floating centered dialogs, draggable |
| **TextArea** | `TextArea` — full multi-line editor (Emacs bindings, undo/redo, search) |
| **ScrollView** | `ScrollView`, `ScrollViewState` — scrollable content viewport |
| **QR codes** | `QrCodeWidget`, `QrColors` — terminal QR codes via Unicode half-blocks |
| **Calendar** | `Monthly`, `CalendarDate`, `CalendarEventStore` — monthly calendar widget |
| **Web TUI** | `pyratatui.ratxilla.WebTerminal` — render in browser via HTTP + WebSocket |
| **Type stubs** | Complete `.pyi` for IDE completion and mypy |

---

## Layout & Widgets

```python
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Block, Paragraph, Gauge, List, ListItem, ListState,
    Table, Row, Cell, TableState, Style, Color,
)

with Terminal() as term:
    list_state = ListState()
    while True:
        def ui(frame):
            chunks = (
                Layout()
                .direction(Direction.Vertical)
                .constraints([Constraint.length(3), Constraint.fill(1), Constraint.length(1)])
                .split(frame.area)
            )
            frame.render_widget(
                Paragraph.from_string("My App").centered()
                    .block(Block().bordered().title(" Header ")),
                chunks[0],
            )
            frame.render_stateful_list(
                List([ListItem("Item A"), ListItem("Item B"), ListItem("Item C")]),
                chunks[1],
                list_state,
            )
            frame.render_widget(
                Paragraph.from_string("  q: quit  ↑/↓: navigate"),
                chunks[2],
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev:
            if ev.code == "q": break
            elif ev.code == "Down": list_state.select_next()
            elif ev.code == "Up":   list_state.select_previous()
```

---

## Async

```python
import asyncio
from pyratatui import AsyncTerminal, Paragraph, Block, Style, Color

async def main():
    tick = 0
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=30, stop_on_quit=True):
            tick += 1
            def ui(frame, t=tick):
                frame.render_widget(
                    Paragraph.from_string(f"Tick {t} — press q to quit")
                        .block(Block().bordered())
                        .style(Style().fg(Color.green())),
                    frame.area,
                )
            term.draw(ui)

asyncio.run(main())
```

---

## Calendar Widget

```python
from pyratatui import (
    CalendarDate, CalendarEventStore, Monthly,
    Block, Style, Color, Terminal,
)

# Mark dates with styles
store = CalendarEventStore.today_highlighted(Style().fg(Color.green()).bold())
store.add(CalendarDate.from_ymd(2024, 12, 25), Style().fg(Color.red()).bold())

# Build the Monthly widget
cal = (
    Monthly(CalendarDate.today(), store)
    .block(Block().bordered().title(" December 2024 "))
    .show_month_header(Style().bold().fg(Color.cyan()))
    .show_weekdays_header(Style().italic())
    .show_surrounding(Style().dim())
    .default_style(Style().fg(Color.white()))
)

with Terminal() as term:
    term.draw(lambda frame: frame.render_widget(cal, frame.area))
    term.poll_event(timeout_ms=10_000)
```

Run the interactive demo:

```bash
python examples/25_calendar.py
# ←/→: prev/next month   ↑/↓: prev/next year   t: today   q: quit
```

---

## Web TUI

`pyratatui.ratxilla` renders your TUI app in the browser — no WASM compilation needed,
pure Python HTTP + WebSocket server.

```python
from pyratatui.ratxilla import WebTerminal
from pyratatui import Paragraph, Block, Style, Color

counter = 0

def ui(frame):
    frame.render_widget(
        Paragraph.from_string(f"Counter: {counter}")
            .block(Block().bordered().title(" Web TUI "))
            .style(Style().fg(Color.cyan())),
        frame.area,
    )

with WebTerminal(cols=100, rows=30) as term:
    print(f"Open: {term.url}")   # → http://localhost:7700/
    while True:
        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "Up":   counter += 1
            if ev.code == "Down": counter -= 1
            if ev.code == "q":    break
```

One-liner shorthand:

```python
from pyratatui.ratxilla import serve
serve(ui)    # auto-opens browser, blocks until 'q'
```

Run the interactive demo:

```bash
python examples/26_web_counter.py
# Open http://localhost:7700/ in your browser
```

### ratzilla WASM (optional)

For full browser-native rendering without ANSI, build the ratzilla WASM app:

```bash
cargo install --locked trunk
rustup target add wasm32-unknown-unknown
./scripts/build_web.sh --release
# Serves from dist/
```

---

## TachyonFX Animations

```python
from pyratatui import Terminal, Paragraph, Block, EffectManager, Motion, Interpolation

manager = EffectManager()
manager.add(
    "fade",
    "fade_from_fg #000000 300ms; then sweep_in_from_left 500ms",
)

with Terminal() as term:
    start = __import__("time").time()
    while True:
        def ui(frame):
            elapsed = int((__import__("time").time() - start) * 1000)
            frame.render_widget(
                Paragraph.from_string("Animated!").block(Block().bordered()),
                frame.area,
            )
            frame.apply_effect_manager(manager, elapsed, frame.area)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=16)
        if ev and ev.code == "q":
            break
```

---

## QR Code Widget

```python
from pyratatui import QrCodeWidget, QrColors, Block, Terminal

qr = QrCodeWidget("https://ratatui.rs").colors(QrColors.Inverted)

with Terminal() as term:
    while True:
        def ui(frame, _qr=qr):
            blk = Block().bordered().title(" QR Code ")
            inner = blk.inner(frame.area)
            frame.render_widget(blk, frame.area)
            frame.render_qrcode(_qr, inner)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=30_000)
        if ev and ev.code in ("q", "Esc"):
            break
```

---

## TextArea Editor

```python
from pyratatui import TextArea, CursorMove, Block, Terminal

ta = TextArea.from_lines(["Edit this text...", "Line two"])
ta.set_block(Block().bordered().title(" Editor "))

with Terminal() as term:
    while True:
        def ui(frame, _ta=ta):
            frame.render_textarea(_ta, frame.area)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev:
            if ev.ctrl and ev.code == "c":
                break
            ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)
```

---

## ScrollView

```python
from pyratatui import ScrollView, ScrollViewState, Terminal

lines = [f"Line {i:>4}:  " + "█" * (i % 40) for i in range(200)]
state = ScrollViewState()

with Terminal() as term:
    while True:
        def ui(frame, _lines=lines):
            sv = ScrollView.from_lines(_lines, content_width=80)
            frame.render_stateful_scrollview(sv, frame.area, state)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev:
            if ev.code == "q":    break
            elif ev.code == "Down": state.scroll_down(1)
            elif ev.code == "Up":   state.scroll_up(1)
```

---

## Cheat Sheet

```python
# Style
Style().fg(Color.cyan()).bg(Color.black()).bold().italic().dim()

# Layout (always use lowercase constraint methods)
Layout().direction(Direction.Vertical).constraints([
    Constraint.length(3),
    Constraint.fill(1),
    Constraint.percentage(30),
    Constraint.min(5),
    Constraint.max(20),
]).split(frame.area)

# Block with inner area
blk   = Block().bordered().title(" Panel ")
inner = blk.inner(area)          # Rect minus borders
frame.render_widget(blk, area)
frame.render_widget(content, inner)

# Table (correct builder pattern)
Table([Row([Cell("A"), Cell("B")])]).column_widths([
    Constraint.fill(1), Constraint.length(8)
]).header(Row([Cell("Name"), Cell("Value")]))

# Calendar
Monthly(CalendarDate.today(), CalendarEventStore.today_highlighted(
    Style().fg(Color.green()).bold()
)).show_month_header(Style().bold())

# QR code
frame.render_qrcode(QrCodeWidget("https://example.com"), area)

# ScrollView
frame.render_stateful_scrollview(ScrollView.from_lines(lines, 80), area, state)

# TextArea
frame.render_textarea(ta, area)

# Web TUI
with WebTerminal(cols=120, rows=35) as term: ...
```

---

## Examples

| # | File | Demonstrates |
|---|------|--------------|
| 01 | `01_hello_world.py` | `Terminal`, `Paragraph`, `Block`, `Style`, `Color` |
| 02 | `02_layout.py` | `Layout`, `Constraint`, `Direction` |
| 03 | `03_styled_text.py` | `Span`, `Line`, `Text`, `Modifier` |
| 04 | `04_list_navigation.py` | `List`, `ListState`, keyboard navigation |
| 05 | `05_progress_bar.py` | `Gauge`, `LineGauge`, live updates |
| 06 | `06_table_dynamic.py` | `Table`, `TableState`, dynamic rows |
| 07 | `07_async_reactive.py` | `AsyncTerminal`, asyncio, reactive data |
| 08 | `08_effects_fade.py` | `EffectManager`, fade-in/out |
| 09 | `09_effects_dsl.py` | `compile_effect` DSL |
| 10 | `10_full_app.py` | Multi-tab app with all widgets |
| 11 | `11_popup_basic.py` | `Popup` (stateless centered) |
| 12 | `12_popup_stateful.py` | `PopupState` (draggable) |
| 13 | `13_popup_scrollable.py` | Scrollable popup content |
| 14 | `14_textarea_basic.py` | `TextArea` basics (Emacs bindings) |
| 15 | `15_textarea_advanced.py` | `TextArea` Vim modal mode |
| 16 | `16_scrollview.py` | `ScrollView`, `ScrollViewState` |
| 17 | `17_qrcode.py` | `QrCodeWidget`, `QrColors` |
| 18 | `18_async_progress.py` | `AsyncTerminal` + async progress |
| 19 | `19_effects_glitch.py` | Glitch effects |
| 20 | `20_effects_matrix.py` | Matrix rain effect |
| 21 | `21_prompt_confirm.py` | `PasswordPrompt` |
| 22 | `22_prompt_select.py` | Select prompt |
| 23 | `23_prompt_text.py` | `TextPrompt` |
| 24 | `24_dashboard.py` | Full monitoring dashboard |
| **25** | **`25_calendar.py`** | **`Monthly`, `CalendarEventStore`, navigation** |
| **26** | **`26_web_counter.py`** | **`pyratatui.ratxilla`, browser TUI** |

---

## Project Structure

```
pyratatui/
├── Cargo.toml              # Rust package (version 0.2.1)
├── pyproject.toml          # Python package metadata
├── src/                    # Rust → Python bindings (PyO3)
│   ├── lib.rs              # Extension module entry point
│   ├── terminal/           # Terminal, Frame, KeyEvent
│   ├── widgets/            # Block, Paragraph, List, Table, Monthly, …
│   ├── style/              # Color, Modifier, Style
│   ├── text/               # Span, Line, Text
│   ├── layout/             # Rect, Constraint, Direction, Layout
│   ├── effects/            # TachyonFX bindings
│   ├── popups/             # Popup, PopupState, KnownSizeWrapper
│   ├── textarea/           # TextArea, CursorMove, Scrolling
│   ├── scrollview/         # ScrollView, ScrollViewState
│   └── qrcode/             # QrCodeWidget, QrColors
├── python/pyratatui/
│   ├── __init__.py         # Python re-exports
│   ├── __init__.pyi        # Complete type stubs
│   ├── async_terminal.py   # AsyncTerminal
│   ├── helpers.py          # run_app, run_app_async
│   └── web/                # pyratatui.ratxilla module
│       ├── __init__.py     # WebTerminal, serve()
│       └── server.py       # HTTP + WebSocket server
├──                 # ratzilla WASM companion app (optional)
│   ├── Cargo.toml
│   ├── index.html
│   └── src/main.rs
├── examples/               # 26 numbered examples (01–26)
├── docs/                   # MkDocs Material documentation
├── scripts/                # Build helpers
│   ├── build.sh / build.ps1
│   └── build_web.sh        # WASM build (requires trunk)
└── tests/
    ├── python/             # pytest
    └── rust/               # cargo test
```

---

## Contributing

```bash
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui
python -m venv .venv && source .venv/bin/activate
pip install maturin pytest pytest-asyncio ruff mypy
maturin develop
pytest tests/python/
cargo test
```

Linting / formatting:

```bash
ruff check .
ruff format .
cargo fmt
cargo clippy -- -D warnings
```

---

## License

MIT — see [LICENSE](LICENSE)

Built with [ratatui](https://ratatui.rs) 🐀 and [PyO3](https://pyo3.rs) 🦀
