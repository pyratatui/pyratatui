# pyratatui

**Python bindings for [ratatui](https://ratatui.rs) 0.29 — high-performance terminal UIs, from Python.**

[![PyPI](https://img.shields.io/pypi/v/pyratatui)](https://pypi.org/project/pyratatui)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![ratatui 0.29](https://img.shields.io/badge/ratatui-0.29-orange)](https://ratatui.rs)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/pyratatui/pyratatui/blob/main/LICENSE)

---

pyratatui wraps the full ratatui 0.29 widget library and the **tachyonfx** animation engine behind a clean, typed, idiomatic Python API compiled with [PyO3](https://pyo3.rs) and [Maturin](https://github.com/PyO3/maturin). No runtime dependencies beyond a Rust toolchain at build time — the wheel ships a self-contained native extension.

## What You Can Build

```
┌─────────────────────────────────────────────────────────┐
│  pyratatui Full App            tick=42                   │
├──────────────┬──────────────────────────────────────────┤
│  Services    │  CPU Usage ████████████░░░░░░░░  68%      │
│  ▶ nginx     │  Memory    ██████░░░░░░░░░░░░░░  32%      │
│    postgres  │                                           │
│    redis     │  CPU History (30 ticks)                   │
│    kafka     │  ▁▂▄▆█▇▅▃▂▁▂▄▅▇█▆▄▂▁▃▅▇▆▄▃▂▁▂▄▅          │
│    prometheus│                                           │
│    alertmgr  │  Requests:  482,910                       │
└──────────────┴──────────────────────────────────────────┘
│  ↑/↓: Navigate  Tab: Switch tab  r: Refresh  q: Quit    │
└─────────────────────────────────────────────────────────┘
```

## Feature Highlights

| Feature | Details |
|---|---|
| **Widgets** | Block, Paragraph, List, Table, Gauge, LineGauge, BarChart, Sparkline, Tabs, Scrollbar, Clear |
| **Layout** | Constraint-based splits (length, percentage, fill, min, max, ratio), flex modes, margins, spacing |
| **Styling** | 16 named colors + 256-indexed + true-color RGB, 9 text modifiers, builder API |
| **Text** | Span → Line → Text hierarchy with per-span styling and alignment |
| **Async** | `AsyncTerminal` with `async for ev in term.events(fps=30)` loop |
| **Effects** | tachyonfx 0.11 — fade, dissolve, coalesce, slide, sweep, sequence, parallel, ping-pong |
| **Events** | Full keyboard event bridge: key codes, Ctrl/Alt/Shift modifiers |
| **Type stubs** | Complete `.pyi` stubs for IDE completion and mypy |

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

## Async Quick Start

```python
import asyncio
from pyratatui import AsyncTerminal, Paragraph, Block, Style, Color

async def main():
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=30):
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
- **[Minimal Examples](examples/minimal_examples.md)** — 10 copy-paste demos
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
  └── re-exports from _pyratatui
      │
      ▼
 _pyratatui (PyO3 native extension)
  ├── Terminal / Frame       # screen driver + render callback
  ├── Layout / Rect / Constraint
  ├── Widgets (Block, Paragraph, List, Table, …)
  ├── Style / Color / Modifier
  ├── Text / Line / Span
  ├── Buffer                 # raw cell grid
  └── Effects (TachyonFX)   # post-render animations
      │
      ▼
 ratatui 0.29 (Rust)        # actual rendering engine
 crossterm                   # cross-platform terminal backend
 tachyonfx 0.11              # animation shaders
```
