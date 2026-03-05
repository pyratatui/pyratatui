# 🌟🚀💎 pyratatui 🐍⚡🔥

<img src="https://github.com/pyratatui/pyratatui/raw/main/gallery/pyratatui.png" 
     alt="PyRatatui Logo" width="100">

**✨🚀💫 Maturin-based Python bindings for [ratatui](https://ratatui.rs) 0.29 🦀🌈🔥**

[![GitHub](https://img.shields.io/badge/GitHub-pyratatui%2Fpyratatui-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/pyratatui/pyratatui)
&nbsp;
[![PyPI](https://img.shields.io/pypi/v/pyratatui?style=flat-square&logo=pypi&color=3775A9)](https://pypi.org/project/pyratatui/)
&nbsp;
[![Downloads](https://img.shields.io/pypi/dm/pyratatui?style=flat-square&color=2ecc71&label=Downloads%2FMonth)](https://pypi.org/project/pyratatui/)
&nbsp;
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
&nbsp;
![Rust](https://img.shields.io/badge/Rust-000000?style=flat-square&logo=rust&logoColor=white)
&nbsp;
[![License](https://img.shields.io/github/license/pyratatui/pyratatui?style=flat-square)](https://github.com/pyratatui/pyratatui/blob/main/LICENSE)
&nbsp;
[![Stars](https://img.shields.io/github/stars/pyratatui/pyratatui?style=flat-square&color=f1c40f)](https://github.com/pyratatui/pyratatui/stargazers)

---

<img src="https://github.com/pyratatui/pyratatui/raw/main/gallery/image.png" 
     alt="Demo">

---

**💖🌟🌈 Partnered with: Alacritty 🔥⚡✨**  

<img src="https://github.com/pyratatui/pyratatui/raw/main/gallery/alacritty.png" 
     alt="Alacritty" width="100">

---

[![CI](https://img.shields.io/github/actions/workflow/status/pyratatui/pyratatui/ci.yml?style=for-the-badge)](https://github.com/pyratatui/pyratatui/actions)  
[![PyPI](https://img.shields.io/pypi/v/pyratatui?style=for-the-badge)](https://pypi.org/project/pyratatui/)  
[![Python](https://img.shields.io/pypi/pyversions/pyratatui?style=for-the-badge)](https://www.python.org/)  
[![License](https://img.shields.io/github/license/pyratatui/pyratatui?style=for-the-badge)](LICENSE)

pyratatui bridges Rust's ultra-fast terminal rendering engine 🦀💨 with Python's ergonomic and productive ecosystem 🐍💡💎.

- Native Rust rendering via **ratatui 0.29** ⚡🚀
- Fully **Pythonic API** — fluent builders, snake_case, type stubs 🐍✨
- **Async-ready** — `AsyncTerminal` integrates seamlessly with asyncio ⚡💻
- **Zero Rustisms** in Python API ✅
- **ABI3 wheels** — one wheel per OS/arch, Python 3.10–3.13+ 💎🌟

---

## Installation 💾🛠️

```bash
pip install pyratatui 🔥
```

Build from source (requires Rust stable + maturin 🦀):

```bash
pip install maturin
maturin develop --release 🚀
```

---

## Hello World 👋🐀✨

```python
from pyratatui import Terminal, Paragraph, Block, Style, Color

with Terminal() as term:
    while True:
        def ui(frame):
            frame.render_widget(
                Paragraph.from_string("Hello, pyratatui! 🐀💖")
                    .block(Block().bordered().title("Demo 🚀✨"))
                    .style(Style().fg(Color.cyan())),
                frame.area,
            )
        term.draw(ui)
        ev = term.poll_event(timeout_ms=100)
        if ev and ev.code == "q":
            break 🛑
```

---

## Layout & Widgets 📊🖌️💎

```python
from pyratatui import (
    Terminal, Layout, Constraint, Direction,
    Block, Paragraph, Gauge, List, ListItem, ListState,
    Table, Row, Cell, TableState,
    Style, Color,
)

with Terminal() as term:
    list_state = ListState()
    list_state.select(0)
    table_state = TableState()
    table_state.select(0)

    while True:
        def ui(frame):
            chunks = Layout().direction(Direction.Vertical).constraints([
                Constraint.length(3),
                Constraint.fill(1),
                Constraint.length(3),
            ]).split(frame.area)

            frame.render_widget(Block().bordered().title("pyratatui Dashboard 📊💡"), chunks[0])

            body = Layout().direction(Direction.Horizontal).constraints([
                Constraint.percentage(40), Constraint.fill(1)
            ]).split(chunks[1])

            items = [ListItem(f"Server {i+1} ⚡💻") for i in range(8)]
            frame.render_stateful_list(
                List(items)
                    .block(Block().bordered().title("Servers 🖥️🌟"))
                    .highlight_style(Style().fg(Color.yellow()).bold())
                    .highlight_symbol("▶✨"),
                body[0],
                list_state,
            )

            header = Row([Cell("Name 🏷️"), Cell("CPU 💻"), Cell("Mem 🧠")])
            rows = [Row.from_strings(["nginx ⚡", "0.2% 🔹", "128MB 💾"]),
                    Row.from_strings(["redis ⚡", "0.1% 🔹", "64MB 💾"])]
            frame.render_stateful_table(
                Table(rows, [Constraint.fill(1)]*3, header=header)
                    .block(Block().bordered().title("Processes 🧮💎"))
                    .highlight_style(Style().fg(Color.cyan())),
                body[1],
                table_state,
            )

            frame.render_widget(
                Gauge().percent(72).label("CPU: 72% 💚⚡")
                    .style(Style().fg(Color.green()))
                    .block(Block().bordered()),
                chunks[2],
            )

        term.draw(ui)
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q": break
            elif ev.code == "Down": list_state.select_next()
            elif ev.code == "Up": list_state.select_previous()
```

---

## Async Usage ⚡💻🚀

```python
import asyncio
from pyratatui import AsyncTerminal, Paragraph, Block, Style, Color

async def main():
    tick = 0
    async with AsyncTerminal() as term:
        async for ev in term.events(fps=30):
            def ui(frame, t=tick):
                frame.render_widget(
                    Paragraph.from_string(f"Tick: {t} ⏱️✨")
                        .block(Block().bordered().title("Async 🚀💡"))
                        .style(Style().fg(Color.magenta())),
                    frame.area,
                )
            term.draw(ui)
            tick += 1

asyncio.run(main())
```

---

## API Overview 📚🛠️✨

| Module      | Types                                                                 |
|-------------|-----------------------------------------------------------------------|
| style       | `Color`, `Modifier`, `Style` 🖌️💎                                      |
| text        | `Span`, `Line`, `Text` ✍️✨                                            |
| layout      | `Rect`, `Constraint`, `Direction`, `Alignment`, `Layout` 🧩💡           |
| buffer      | `Buffer` 🔹⚡                                                           |
| widgets     | `Block`, `Paragraph`, `List`, `Table`, `Gauge`, `LineGauge`, ... 🛠️🚀 |
| terminal    | `Terminal`, `Frame`, `KeyEvent` 🎛️💎                                    |
| async       | `AsyncTerminal`, `run_app`, `run_app_async` ⚡💻                        |
| errors      | `PyratatuiError`, `BackendError`, `LayoutError`, `RenderError`, ... ❌🔥|

Full reference: [https://pyratatui.github.io/pyratatui](https://pyratatui.github.io/pyratatui)

---

## Contributing 🤝✨💡

```bash
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui
python -m venv .venv && source .venv/bin/activate
pip install maturin pytest pytest-asyncio ruff mypy
maturin develop
pytest tests/python/
cargo test 🚀
```

---

## License 📜💎

MIT — see [LICENSE](LICENSE)

Built with [ratatui](https://ratatui.rs) 🐀💨 and [PyO3](https://pyo3.rs) 🦀⚡

---

