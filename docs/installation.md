# Installation

## Requirements

- Python **3.10** or later
- No Rust required for end-users (pre-built ABI3 wheels are provided)

## From PyPI (Recommended)

```bash
pip install pyratatui
```

Wheels are available for Linux (manylinux2014), macOS (x86_64 and Apple Silicon), and Windows.

## From Source

You need Rust stable and maturin:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
pip install maturin
```

Then build and install:

```bash
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui
maturin develop --release   # editable install in current venv
# or
maturin build --release     # produces a wheel in dist/
pip install dist/pyratatui-*.whl
```

## Development Install

```bash
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install maturin pytest pytest-asyncio ruff mypy
maturin develop
```

## Verify

```python
import pyratatui
print(pyratatui.__version__)
print(pyratatui.__ratatui_version__)
```

## Optional Extras

```bash
pip install "pyratatui[dev]"   # adds pytest, ruff, mypy
pip install "pyratatui[docs]"  # adds mkdocs + mkdocstrings
```
