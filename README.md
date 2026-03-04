# pyratatui 🐀

**Production-grade Python bindings for [ratatui](https://ratatui.rs) 0.30.0**

[![CI](https://github.com/pyratatui/pyratatui/actions/workflows/ci.yml/badge.svg)](https://github.com/pyratatui/pyratatui/actions)
[![PyPI](https://img.shields.io/pypi/v/pyratatui.svg)](https://pypi.org/project/pyratatui/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

pyratatui is a language bridge between Rust's high-performance terminal rendering engine
and Python's ergonomic, productive ecosystem.

- All rendering is native Rust via **ratatui 0.30.0**
- Python gets a fully **Pythonic API** — fluent builders, snake_case, type stubs
- **Async ready** — `AsyncTerminal` integrates with asyncio seamlessly
- **Zero Rustisms** in the public API
- **ABI3 wheels** — one wheel per OS/arch, runs on Python 3.10–3.13+

---

## Installation

```bash
pip install pyratatui
```

For building from source, you need Rust stable and maturin:

```bash
pip install maturin
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
                Paragraph.from_string("Hello, pyratatui! 🐀")
                    .block(Block().bordered().title("Demo"))
                    .style(Style().fg(Color.cyan())),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

---

## Layout + Widgets

```python
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Block, Paragraph, Gauge, List, ListItem, ListState,
    Table, Row, Cell, TableState,
    Style, Color, Text,
)

with Terminal() as term:
    list_state = ListState()
    list_state.select(0)
    table_state = TableState()
    table_state.select(0)

    while True:
        def ui(frame):
            # Split vertically: header | body | footer
            chunks = (Layout()
                .direction(Direction.Vertical)
                .constraints([
                    Constraint.length(3),
                    Constraint.fill(1),
                    Constraint.length(3),
                ])
                .split(frame.area))

            # Header
            frame.render_widget(
                Block().bordered().title("pyratatui Dashboard"),
                chunks[0],
            )

            # Body: split horizontally
            body = (Layout()
                .direction(Direction.Horizontal)
                .constraints([Constraint.percentage(40), Constraint.fill(1)])
                .split(chunks[1]))

            # Left: list
            items = [ListItem(f"Server {i+1}") for i in range(8)]
            frame.render_stateful_list(
                List(items)
                    .block(Block().bordered().title("Servers"))
                    .highlight_style(Style().fg(Color.yellow()).bold())
                    .highlight_symbol("▶ "),
                body[0],
                list_state,
            )

            # Right: table
            header = Row([Cell("Name"), Cell("CPU"), Cell("Mem")])
            rows   = [Row.from_strings(["nginx", "0.2%", "128MB"]),
                      Row.from_strings(["redis", "0.1%", "64MB"])]
            frame.render_stateful_table(
                Table(rows, [Constraint.fill(1)] * 3, header=header)
                    .block(Block().bordered().title("Processes"))
                    .highlight_style(Style().fg(Color.cyan())),
                body[1],
                table_state,
            )

            # Footer: gauge
            frame.render_widget(
                Gauge().percent(72).label("CPU: 72%")
                    .style(Style().fg(Color.green()))
                    .block(Block().bordered()),
                chunks[2],
            )

        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q": break
            elif ev.code == "Down": list_state.select_next()
            elif ev.code == "Up":  list_state.select_previous()
```

---

## Async Usage

```python
import asyncio
from pyratatui import AsyncTerminal, Paragraph, Block, Style, Color

async def main():
    tick = 0
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=30):
            def ui(frame, t=tick):
                frame.render_widget(
                    Paragraph.from_string(f"Tick: {t}")
                        .block(Block().bordered().title("Async"))
                        .style(Style().fg(Color.magenta())),
                    frame.area,
                )
            term.draw(ui)
            tick += 1

asyncio.run(main())
```

---

## API Overview

| Module      | Types                                                                 |
|-------------|-----------------------------------------------------------------------|
| style       | `Color`, `Modifier`, `Style`                                         |
| text        | `Span`, `Line`, `Text`                                               |
| layout      | `Rect`, `Constraint`, `Direction`, `Alignment`, `Layout`             |
| buffer      | `Buffer`                                                             |
| widgets     | `Block`, `Paragraph`, `List`, `Table`, `Gauge`, `LineGauge`, ...     |
| terminal    | `Terminal`, `Frame`, `KeyEvent`                                      |
| async       | `AsyncTerminal`, `run_app`, `run_app_async`                          |
| errors      | `PyratatuiError`, `BackendError`, `LayoutError`, `RenderError`, ...  |

Full API reference: [https://pyratatui.github.io/pyratatui](https://pyratatui.github.io/pyratatui)

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

---

## License

MIT — see [LICENSE](LICENSE).

---

Built with [ratatui](https://ratatui.rs) 🐀 and [PyO3](https://pyo3.rs) 🦀
