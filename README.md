# 🌟🚀💎 pyratatui 🐍⚡🔥

<img src="https://github.com/pyratatui/pyratatui/raw/main/gallery/pyratatui.png" 
     alt="PyRatatui Logo" width="100">

**✨🚀💫 Maturin-based Python bindings for [ratatui](https://ratatui.rs) 0.30 🦀🌈🔥**

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

| ![Demo 1](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_1.png) | ![Demo 2](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_2.png) |
|---|---|
| ![Demo 3](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_3.png) | ![Demo 4](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_4.png) |
| ![Demo 5](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_5.png) | ![Demo 6](https://github.com/pyratatui/pyratatui/raw/main/gallery/snip_6.png) |

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

- Native Rust rendering via **ratatui 0.30** ⚡🚀
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
| effects     | `Effect`, `EffectManager`, `CellFilter`, `Interpolation`, ... 🌈✨     |
| prompts     | `TextPrompt`, `PasswordPrompt`, `TextState`, `PromptStatus` 💬💡       |
| **popups**  | **`Popup`, `PopupState`, `KnownSizeWrapper`** 🪟✨                      |
| **textarea**| **`TextArea`, `CursorMove`, `Scrolling`** ✏️🔥                          |
| **scrollview** | **`ScrollView`, `ScrollViewState`** 📜⚡                            |
| **qrcode**  | **`QrCodeWidget`, `QrColors`** 📱🔲                                     |
| errors      | `PyratatuiError`, `BackendError`, `LayoutError`, `RenderError`, ... ❌🔥|

Full reference: [https://pyratatui.github.io/pyratatui](https://pyratatui.github.io/pyratatui)

---

## TextArea ✏️🔥

A full-featured multi-line text editor widget powered by [`tui-textarea`](https://crates.io/crates/tui-textarea):

```python
from pyratatui import TextArea, CursorMove, Block, Style, Color, Terminal

ta = TextArea.from_lines(["Hello", "World"])
ta.set_block(Block().bordered().title(" Editor "))
ta.set_line_number_style(Style().fg(Color.dark_gray()))
ta.set_cursor_line_style(Style().bg(Color.dark_gray()))

with Terminal() as term:
    while True:
        term.draw(lambda frame: frame.render_textarea(ta, frame.area))
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "Esc": break
            ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)

print("\n".join(ta.lines()))
```

| TextArea method | Description |
|---|---|
| `TextArea.from_lines(lines)` | Create with initial content |
| `input_key(code, ctrl, alt, shift)` | Process key with Emacs bindings |
| `move_cursor(CursorMove.*)` | Programmatic cursor movement |
| `undo()` / `redo()` | Undo/redo history |
| `lines()` | Get all text lines |
| `set_block(block)` | Add border/title |
| `set_line_number_style(style)` | Enable line numbers |

---

## ScrollView 📜⚡

Scrollable viewport for oversized content, powered by [`tui-scrollview`](https://crates.io/crates/tui-scrollview):

```python
from pyratatui import ScrollView, ScrollViewState, Terminal

lines = [f"  {i:03d} │ " + "data " * 10 for i in range(200)]
state = ScrollViewState()

with Terminal() as term:
    while True:
        sv = ScrollView.from_lines(lines, content_width=80)
        term.draw(lambda frame: frame.render_stateful_scrollview(sv, frame.area, state))
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "q":        break
            elif ev.code == "Down":   state.scroll_down(1)
            elif ev.code == "Up":     state.scroll_up(1)
            elif ev.code == "Home":   state.scroll_to_top()
            elif ev.code == "End":    state.scroll_to_bottom()
```

---

## QrCodeWidget 📱🔲

Render scannable QR codes natively in the terminal using Unicode half-block characters
(`▀` `▄` `█` `space`). QR codes are encoded with the `qrcode` crate and painted
directly into the ratatui frame buffer — no external process or image renderer needed.

> **Implementation note:** pyratatui uses native Unicode half-block rendering rather
> than `tui-qrcode`, which depends on a pre-release ratatui API. The result is
> pixel-perfect and fully compatible with ratatui 0.30.

```python
from pyratatui import QrCodeWidget, QrColors, Block, Terminal

qr = QrCodeWidget("https://ratatui.rs").colors(QrColors.Inverted)

with Terminal() as term:
    while True:
        def ui(frame):
            block = Block().bordered().title(" QR Code ")
            inner = block.inner(frame.area)
            frame.render_widget(block, frame.area)
            frame.render_qrcode(qr, inner)
        term.draw(ui)
        ev = term.poll_event(timeout_ms=30_000)
        if ev and ev.code == "q":
            break
```

| QrCodeWidget method | Description |
|---|---|
| `QrCodeWidget(data)` | Encode string as QR code |
| `.colors(QrColors.Default)` | Dark on light (standard) |
| `.colors(QrColors.Inverted)` | Light on dark (suits dark terminals) |
| `.quiet_zone(n)` | Quiet zone border size in modules (default 2) |

`frame.render_qrcode(qr, area)` — renders into a `Rect`. Use `Block.inner(area)`
to compute the inner area when wrapping in a border.

---

## Popups 🪟✨

pyratatui integrates the [`tui-popup`](https://crates.io/crates/tui-popup)
crate for professional centered popup dialogs.

```python
from pyratatui import Popup, PopupState, KnownSizeWrapper, Style, Color, Terminal

# ── Basic centered popup ───────────────────────────────────────────────────────
popup = (
    Popup("Press any key to exit.")
    .title(" tui-popup demo ")
    .style(Style().fg(Color.white()).bg(Color.blue()))
)

with Terminal() as term:
    term.draw(lambda frame: frame.render_popup(popup, frame.area))
    term.poll_event(timeout_ms=5000)

# ── Draggable popup with PopupState ───────────────────────────────────────────
state = PopupState()

with Terminal() as term:
    while True:
        term.draw(lambda frame: frame.render_stateful_popup(popup, frame.area, state))
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "Up":    state.move_up(1)
            if ev.code == "Down":  state.move_down(1)
            if ev.code == "Esc":   break

# ── Scrollable popup with KnownSizeWrapper ────────────────────────────────────
lines = [f"Item {i:03d}: some content" for i in range(50)]
wrapper = KnownSizeWrapper(lines, width=40, height=10)

scrollable_popup = Popup(wrapper).title(" Scrollable ")
with Terminal() as term:
    while True:
        term.draw(lambda frame: frame.render_popup(scrollable_popup, frame.area))
        ev = term.poll_event(timeout_ms=50)
        if ev:
            if ev.code == "Up":   wrapper.scroll_up(1)
            if ev.code == "Down": wrapper.scroll_down(1)
            if ev.code == "Esc":  break
```

### Popup API

| Method | Description |
|--------|-------------|
| `Popup(content)` | Create popup; content is `str` or `KnownSizeWrapper` |
| `.title(title)` | Set border title (builder) |
| `.style(style)` | Set colors/style (builder) |
| `frame.render_popup(popup, area)` | Render stateless (centered) |
| `frame.render_stateful_popup(popup, area, state)` | Render stateful (draggable) |

| `PopupState` method | Description |
|---------------------|-------------|
| `move_up/down/left/right(n)` | Move popup by n cells |
| `move_to(x, y)` | Move to absolute position |
| `mouse_down/up/drag(col, row)` | Handle mouse drag events |
| `reset()` | Return popup to center |

| `KnownSizeWrapper` | Description |
|--------------------|-------------|
| `KnownSizeWrapper(lines, width, height)` | Create with fixed dimensions |
| `scroll_down(n)` / `scroll_up(n)` | Scroll content |
| `.scroll` | Current scroll offset |



---

## Examples 📁

All examples are in the `examples/` directory. Run any with `python examples/<name>.py`.

| File | Description |
|------|-------------|
| `01_hello_world.py` | Minimal hello world — Terminal, Paragraph, Block, Style, Color |
| `02_layout.py` | Horizontal & vertical layouts with Constraint variants |
| `03_styled_text.py` | Styled spans, bold/italic/underline, Color palette |
| `04_list_navigation.py` | Scrollable list with ListState selection |
| `05_progress_bar.py` | Gauge, LineGauge, Sparkline live updates |
| `06_table_dynamic.py` | Dynamic table with TableState — `Table(rows).column_widths([...]).header(row)` |
| `07_async_reactive.py` | AsyncTerminal with asyncio tasks and reactive updates |
| `08_effects_fade.py` | TachyonFX fade-in/out effects |
| `09_effects_dsl.py` | TachyonFX DSL chaining — sweep, translate, coalesce |
| `10_full_app.py` | Multi-panel dashboard — list + table + gauge + popup |
| `11_popup_basic.py` | Basic centered popup (tui-popup) |
| `12_popup_stateful.py` | Draggable popup with PopupState |
| `13_popup_scrollable.py` | Popup with scrollable content via KnownSizeWrapper |
| `14_textarea_basic.py` | Simple text editor with tui-textarea |
| `15_textarea_advanced.py` | Vim-style modal editing with tui-textarea |
| `16_scrollview.py` | Large scrollable viewport — `Block.inner(area)` + tui-scrollview |
| `17_qrcode.py` | QR code in terminal — Unicode half-block rendering |
| `18_async_progress.py` | Async progress bars with background task |
| `19_effects_glitch.py` | TachyonFX glitch and pixelate effects |
| `20_effects_matrix.py` | TachyonFX matrix rain effect |
| `21_prompt_confirm.py` | Confirmation prompt widget |
| `22_prompt_select.py` | Selection prompt widget |
| `23_prompt_text.py` | Text input prompt widget |
| `24_dashboard.py` | Complete multi-widget dashboard |

### Key API Patterns

```python
# Layout — use Layout() not Layout.default()
chunks = Layout().direction(Direction.Vertical).constraints([...]).split(frame.area)

# Constraint — always lowercase static methods
Constraint.length(10)   # not Constraint.Length(10)
Constraint.min(0)       # not Constraint.Min(0)
Constraint.fill(1)
Constraint.percentage(50)

# Table — rows first, then chain .column_widths() and .header()
Table(rows).column_widths([Constraint.fill(1), Constraint.length(8)]).header(header_row)

# Block.inner(area) — compute inner Rect after borders (NEW in 0.2.0)
block = Block().bordered().title("My Panel")
inner = block.inner(frame.area)   # subtracts border width/height
frame.render_widget(block, frame.area)
frame.render_widget(content, inner)

# QR codes — render_qrcode(widget, area)
qr = QrCodeWidget("https://example.com").colors(QrColors.Inverted)
frame.render_qrcode(qr, area)

# ScrollView — stateful scrollable viewport
sv = ScrollView.from_lines(lines, content_width=100)
frame.render_stateful_scrollview(sv, inner_area, state)

# TextArea — full-featured editor
ta = TextArea.from_lines(["line 1", "line 2"])
ta.input_key(ev.code, ev.ctrl, ev.alt, ev.shift)
frame.render_textarea(ta, area)
```

---

## Contributing 🤝✨💡

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

## License 📜💎

MIT — see [LICENSE](LICENSE)

Built with [ratatui](https://ratatui.rs) 🐀💨 and [PyO3](https://pyo3.rs) 🦀⚡

---

