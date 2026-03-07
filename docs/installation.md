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

If no wheel is available for your platform, pip falls back to building from
source (requires a Rust toolchain — see below).

---

## Virtual Environment (Recommended)

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

`--release` enables full Rust optimizations (strongly recommended).

### 4. Verify the install

```python
import pyratatui
print(pyratatui.__version__)           # "0.2.1"
print(pyratatui.__ratatui_version__)   # "0.30"
```

---

## Build a Distributable Wheel

```bash
maturin build --release
# Wheel appears in target/wheels/
pip install target/wheels/pyratatui-*.whl
```

See **[Build Scripts](../build/build_scripts.md)** for CI/CD and cross-compilation.

---

## Develop Install (Editable)

```bash
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui
pip install maturin
maturin develop          # debug build (fast compile, slower runtime)
```

After changing Rust source, re-run `maturin develop`. Python files under
`python/pyratatui/` (including `pyratatui.web`) are picked up immediately.

---

## Web TUI — No Extra Dependencies

`pyratatui.web` is pure Python and uses only the standard library:

```python
from pyratatui.web import WebTerminal, serve
```

No `pip install` needed beyond `pyratatui` itself.

### Optional: ratzilla WASM app

The companion `pyratatui.ratxilla (pure-Python, no WASM needed)` provides full browser-native rendering via ratzilla.
Build it with:

```bash
cargo install --locked trunk
rustup target add wasm32-unknown-unknown
./scripts/build_web.sh --release
```

---

## Platform Notes

### Windows

Requires Windows Terminal or VS Code integrated terminal (Windows 10 build 1903+
for VT sequence support). The classic `cmd.exe` may not render all Unicode
characters correctly.

### macOS

The default Terminal.app works but has limited colour support.
[iTerm2](https://iterm2.com) or [Alacritty](https://alacritty.org) are
recommended for true-colour and Unicode.

### Linux

Any modern terminal emulator works. Verify true-colour support with:

```bash
echo $COLORTERM   # should be "truecolor" or "24bit"
```

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'pyratatui._pyratatui'`**

The native extension was not compiled. Run `maturin develop --release` inside
the repo, or reinstall via pip.

**`PanicException: pyratatui::terminal::Terminal is unsendable`**

You called a Terminal method from a thread-pool thread. Use `AsyncTerminal`
instead. See [Async Updates](../tutorial/async_updates.md).

**Garbage on screen after Ctrl-C**

Always use `Terminal` as a context manager. For emergency recovery:
`reset` or `stty sane` in your shell.

**`ValueError: Invalid date`**

`CalendarDate.from_ymd(year, month, day)` raises `ValueError` for invalid dates
such as February 30. Validate inputs before constructing.
