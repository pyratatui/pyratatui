# pyratatui

**Python bindings for [ratatui](https://ratatui.rs) 0.30 — high-performance terminal UIs, from Python.**

[![PyPI](https://img.shields.io/pypi/v/pyratatui)](https://pypi.org/project/pyratatui)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![ratatui 0.30](https://img.shields.io/badge/ratatui-0.30-orange)](https://ratatui.rs)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/pyratatui/pyratatui/blob/main/LICENSE)

---

pyratatui wraps the full ratatui 0.30 widget library — including the built-in
Calendar widget — plus the tachyonfx animation engine and a browser-based web
TUI module behind a clean, typed, idiomatic Python API compiled with
[PyO3](https://pyo3.rs) and [Maturin](https://github.com/PyO3/maturin).
No runtime dependencies beyond the pre-built native extension wheel.

## What You Can Build

```
┌ pyratatui Dashboard ──────────────────────────────────────┐
│ Services    │ CPU  ████████████░░░░░░░░  62%              │
│ ▶ nginx     │ Mem  ██████░░░░░░░░░░░░░░  31%              │
│   postgres  │                                             │
│   redis     │ CPU History                                 │
│   kafka     │ ▁▂▄▆█▇▅▃▂▁▂▄▅▇█▆▄▂▁▃▅▇▆▄▃▂▁▂▄▅             │
├─────────────┴─────────────────────────────────────────────┤
│ ↑/↓: Navigate   Tab: Switch tab   r: Refresh   q: Quit    │
└───────────────────────────────────────────────────────────┘
```

## Feature Highlights

| Feature | Details |
|---|---|
| **Widgets** | Block, Paragraph, List, Table, Gauge, LineGauge, BarChart, Sparkline, Tabs, Scrollbar, Clear, **Monthly** |
| **Layout** | Constraint-based splits (length, percentage, fill, min, max, ratio), flex modes |
| **Styling** | 16 named + 256-indexed + RGB true-colour, 9 text modifiers, immutable builder |
| **Text** | `Span` → `Line` → `Text` hierarchy with per-span styling |
| **Async** | `AsyncTerminal` with `async for ev in term.events(fps=30)` |
| **Effects** | tachyonfx 0.25 — fade, dissolve, coalesce, slide, sweep, sequence, parallel |
| **Prompts** | `TextPrompt`, `PasswordPrompt` with live validation |
| **Popups** | `Popup`, `PopupState` — floating dialogs, draggable |
| **TextArea** | Full multi-line editor with Emacs bindings, undo/redo |
| **ScrollView** | `ScrollView`, `ScrollViewState` — scrollable viewport |
| **QR codes** | `QrCodeWidget` — terminal QR codes via Unicode half-blocks |
| **Calendar** | `Monthly`, `CalendarDate`, `CalendarEventStore` — monthly calendar |
| **Web TUI** | `pyratatui.web.WebTerminal` — render any app in the browser |
| **Type stubs** | Complete `.pyi` for IDE completion and mypy |

## Quick Start

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

## Calendar Quick Start

```python
from pyratatui import CalendarDate, CalendarEventStore, Monthly, Block, Style, Color, Terminal

store = CalendarEventStore.today_highlighted(Style().fg(Color.green()).bold())
cal   = (Monthly(CalendarDate.today(), store)
            .block(Block().bordered())
            .show_month_header(Style().bold().fg(Color.cyan()))
            .show_weekdays_header(Style().italic()))

with Terminal() as term:
    term.draw(lambda frame: frame.render_widget(cal, frame.area))
    term.poll_event(timeout_ms=10_000)
```

## Web TUI Quick Start

```python
from pyratatui.web import serve
from pyratatui import Paragraph, Block

def ui(frame):
    frame.render_widget(
        Paragraph.from_string("Hello, browser!").block(Block().bordered()),
        frame.area,
    )

serve(ui)   # opens browser at http://localhost:7700/, blocks until 'q'
```

## Async Quick Start

```python
import asyncio
from pyratatui import AsyncTerminal, Paragraph, Block, Style, Color

async def main():
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=30, stop_on_quit=True):
            def ui(frame):
                frame.render_widget(
                    Paragraph.from_string("Async pyratatui! Press q to quit.")
                        .block(Block().bordered())
                        .style(Style().fg(Color.green())),
                    frame.area,
                )
            term.draw(ui)

asyncio.run(main())
```

## Navigation

- **[Installation](installation.md)** — pip, build from source, prerequisites
- **[Quickstart Tutorial](tutorial/quickstart.md)** — first app in 5 minutes
- **[Async Updates](tutorial/async_updates.md)** — live reactive UIs
- **[Progress Bar Tutorial](tutorial/progress_bar.md)** — animated progress indicators
- **[TachyonFX Effects](tutorial/tachyonfx_effects.md)** — animations and transitions
- **[API Reference](reference/terminal.md)** — complete class/method documentation
- **[Calendar Reference](reference/calendar.md)** — Calendar widget
- **[Web TUI Reference](reference/web.md)** — browser-based TUI
- **[Minimal Examples](examples/minimal_examples.md)** — copy-paste demos
- **[Advanced Examples](examples/advanced_examples.md)** — full mini-apps
- **[Build & Package](build/build_scripts.md)** — compile and distribute wheels
- **[FAQ](faq.md)** — common questions and troubleshooting

## Architecture Overview

```
Python application
      │
      ▼
pyratatui (Python layer)
  ├── AsyncTerminal          # asyncio wrapper
  ├── run_app / run_app_async # convenience helpers
  └── web/                   # pyratatui.web — browser TUI
      │
      ▼ (re-exports from _pyratatui)
_pyratatui (PyO3 native extension)
  ├── Terminal / Frame       # screen driver + render callback
  ├── Layout / Rect / Constraint
  ├── Widgets
  │   ├── Block, Paragraph, List, Table, Gauge, …
  │   └── Monthly            # Calendar widget (NEW in 0.2.1)
  ├── Style / Color / Modifier
  ├── Text / Line / Span
  ├── Effects (TachyonFX)
  ├── Popup / TextArea / ScrollView / QrCodeWidget
  └── CalendarDate / CalendarEventStore
      │
      ▼
ratatui 0.30 (Rust)         # rendering engine
crossterm 0.29              # cross-platform terminal backend
tachyonfx 0.25              # animation shaders
time 0.3                    # date arithmetic (Calendar)
```
