# pyratatui

**Production-grade Python bindings for [ratatui](https://ratatui.rs) 0.29**

[![CI](https://img.shields.io/github/actions/workflow/status/pyratatui/pyratatui/ci.yml?style=for-the-badge)](https://github.com/pyratatui/pyratatui/actions)

[![PyPI](https://img.shields.io/pypi/v/pyratatui?style=for-the-badge)](https://pypi.org/project/pyratatui/)

[![Python](https://img.shields.io/pypi/pyversions/pyratatui?style=for-the-badge)](https://www.python.org/)

[![Rust](https://img.shields.io/badge/rust-stable-orange?style=for-the-badge&logo=rust)](https://www.rust-lang.org/)

[![License](https://img.shields.io/github/license/pyratatui/pyratatui?style=for-the-badge)](LICENSE)

---

pyratatui brings Rust's blazing-fast terminal rendering engine to Python — with a fully
Pythonic API, complete type stubs, async support, and CI-ready packaging.

## Why pyratatui?

- **Native performance** — all rendering is done by Rust; Python just describes *what* to draw.
- **Pythonic API** — fluent builders, snake_case names, no Rust concepts leaking through.
- **Full ratatui 0.30 surface** — Block, Paragraph, List, Table, Gauge, LineGauge, BarChart, Sparkline, Scrollbar, Tabs, and more.
- **Async ready** — `AsyncTerminal` + `run_app_async()` for asyncio event loops.
- **Typed** — complete `.pyi` stubs bundled; works with mypy and pyright out of the box.
- **ABI3 wheels** — one wheel per platform, compatible with Python 3.10+.

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
                frame.area
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break
```

## Features at a Glance

| Category      | Items                                                     |
|---------------|-----------------------------------------------------------|
| Style         | `Color`, `Modifier`, `Style`                             |
| Text          | `Span`, `Line`, `Text`                                   |
| Layout        | `Rect`, `Constraint`, `Direction`, `Layout`, `Alignment` |
| Widgets       | `Block`, `Paragraph`, `List`, `Table`, `Gauge`, ...      |
| Terminal      | `Terminal`, `Frame`, `AsyncTerminal`                     |
| Errors        | `PyratatuiError` hierarchy                               |
| Types         | Full `.pyi` stubs                                        |
| Async         | `AsyncTerminal`, `run_app_async()`                       |

## Next Steps

- [Installation](installation.md)
- [Quickstart Tutorial](tutorial/quickstart.md)
- [API Reference](reference/terminal.md)
