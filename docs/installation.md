# Installation

## Requirements

| Requirement | Minimum version | Notes |
|---|---|---|
| Python | 3.10 | 3.11+ recommended |
| Operating system | Linux, macOS, Windows | crossterm backend |
| Rust toolchain | 1.75 | only required when building from source |

---

## Install a Pre-built Wheel (Recommended)

```bash
pip install pyratatui
```

Pre-built wheels are available on PyPI for:

- Linux x86\_64 (manylinux2014)
- macOS x86\_64 and arm64 (universal2)
- Windows x86\_64

If a wheel is not available for your platform, pip automatically falls back to building from source (requires a Rust toolchain — see below).

---

## Virtual Environment (Recommended)

Always install into an isolated virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows PowerShell

pip install pyratatui
```

---

## Build from Source

### 1. Install the Rust toolchain

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
rustup update stable
```

### 2. Install Maturin

```bash
pip install maturin
```

### 3. Clone and build

```bash
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui
maturin develop --release   # installs into the current virtualenv
```

`--release` enables full Rust optimizations (strongly recommended for production).

### 4. Verify the install

```python
import pyratatui
print(pyratatui.__version__)           # e.g. "0.1.0"
print(pyratatui.__ratatui_version__)   # "0.29"
```

---

## Build a Distributable Wheel

```bash
maturin build --release
# Wheel appears in target/wheels/
pip install target/wheels/pyratatui-*.whl
```

See **[Build Scripts](../build/build_scripts.md)** for CI/CD automation and cross-compilation.

---

## Develop Install (Editable)

For contributing to pyratatui itself:

```bash
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui
pip install maturin
maturin develop          # debug build — faster compile, slower runtime
```

After changing Rust source, re-run `maturin develop` to recompile. Python files in `python/pyratatui/` are picked up immediately without recompilation.

---

## Platform Notes

### Windows

Requires a Windows terminal that supports VT sequences (Windows Terminal, VS Code integrated terminal, or Windows 10 build 1903+). The classic `cmd.exe` may not render all Unicode characters correctly.

```powershell
pip install pyratatui
python examples/01_hello_world.py
```

### macOS

The default macOS Terminal.app works but has limited color support. [iTerm2](https://iterm2.com) or [Alacritty](https://alacritty.org) are recommended for true-color and Unicode support.

### Linux

Any modern terminal emulator works. For true-color RGB (`Color.rgb(r, g, b)`), verify your terminal with:

```bash
echo $COLORTERM   # should be "truecolor" or "24bit"
```

---

## Verify Your Install

Run the hello-world example directly:

```bash
python -c "
from pyratatui import Terminal, Paragraph, Block
with Terminal() as t:
    t.draw(lambda f: f.render_widget(
        Paragraph.from_string('pyratatui installed!').block(Block().bordered()),
        f.area))
    t.poll_event(timeout_ms=2000)
"
```

You should see a bordered box with the message for 2 seconds.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'pyratatui._pyratatui'`**

The native extension was not compiled. Run `maturin develop --release` inside the repo, or reinstall via pip.

**`PanicException: pyratatui::terminal::Terminal is unsendable`**

You called a Terminal method from a thread-pool thread (e.g. via `asyncio.to_thread` or `loop.run_in_executor`). Use `AsyncTerminal` which always calls Terminal on the main event-loop thread. See [Async Updates](../tutorial/async_updates.md).

**Garbage on screen after Ctrl-C**

The terminal was not restored. Always use `Terminal` as a context manager (`with Terminal() as t:`). For emergency recovery, run `reset` or `stty sane` in your shell.

**Colors look wrong**

Ensure your terminal supports the color mode you are using. Use `Color.indexed()` (0–255) for maximum compatibility, or `Color.rgb()` only in true-color terminals.
