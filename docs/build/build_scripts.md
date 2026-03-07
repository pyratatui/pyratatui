# Build Scripts

pyratatui is compiled with [Maturin](https://github.com/PyO3/maturin) — the standard tool for building PyO3-based Python extensions.

---

## Prerequisites

| Tool | Purpose | Install |
|---|---|---|
| Rust 1.75+ | Compile the extension | `rustup update stable` |
| Maturin | Build & package | `pip install maturin` |
| Python 3.10+ | Runtime + build env | System package manager |

---

## Quick Build (Development)

```bash
# 1. Clone the repo
git clone https://github.com/pyratatui/pyratatui.git
cd pyratatui

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# 3. Install build dependencies
pip install maturin

# 4. Build and install in editable mode
maturin develop              # debug build (fast compile)
maturin develop --release    # optimized build (recommended)
```

After changing Rust source code, re-run `maturin develop` to recompile. Python-only changes (files under `python/`) are picked up immediately.

---

## Build a Release Wheel

```bash
maturin build --release
```

Output: `target/wheels/pyratatui-<version>-<platform>.whl`

```bash
# Install the built wheel
pip install target/wheels/pyratatui-*.whl
```

---

## Linux Convenience Script

```bash
#!/usr/bin/env bash
# scripts/build.sh
set -euo pipefail

echo "Building pyratatui..."
maturin build --release --strip
echo "Build complete. Wheel: target/wheels/"
ls -lh target/wheels/
```

Run with:

```bash
bash scripts/build.sh
```

---

## Windows Convenience Script

```powershell
# scripts/build.ps1
Write-Host "Building pyratatui..."
maturin build --release --strip
Write-Host "Build complete."
Get-ChildItem target/wheels/
```

Run with:

```powershell
.\scripts\build.ps1
```

---

## Build Flags Reference

| Flag | Description |
|---|---|
| `--release` | Enable Rust optimizations (strongly recommended for production) |
| `--strip` | Strip debug symbols from the wheel (smaller file size) |
| `--out <dir>` | Override wheel output directory |
| `--target <triple>` | Cross-compile for a specific target (e.g. `aarch64-unknown-linux-gnu`) |
| `-i python3.11` | Build for a specific Python interpreter |
| `--zig` | Use Zig as the C linker (for better cross-compilation) |

---

## manylinux Wheels (PyPI-Compatible)

Pre-built Linux wheels for PyPI must be compiled with manylinux to ensure broad compatibility. The easiest approach is to use Maturin's Docker images:

```bash
# Build a manylinux2014 wheel (x86_64)
docker run --rm \
  -v "$(pwd)":/io \
  ghcr.io/pyo3/maturin \
  build --release --strip --zig
```

This produces a `*-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` wheel installable on virtually all Linux systems.

---

## macOS Universal2 Wheels

Build a single wheel that runs natively on both Intel and Apple Silicon:

```bash
# Install both targets
rustup target add x86_64-apple-darwin
rustup target add aarch64-apple-darwin

# Build universal2
maturin build --release --strip --target universal2-apple-darwin
```

---

## Cross-Compilation

Build a Linux aarch64 wheel from a macOS host using Zig:

```bash
pip install maturin[zig]
rustup target add aarch64-unknown-linux-gnu

maturin build --release --strip \
  --target aarch64-unknown-linux-gnu \
  --zig
```

---

## Running Tests

```bash
# Rust unit tests
cargo test

# Python integration tests
pip install pytest
pytest tests/
```

---

## CI/CD with GitHub Actions

The repository includes `.github/workflows/ci.yml`. Key jobs:

1. **lint** — `cargo clippy` and `cargo fmt --check`
2. **test** — `cargo test` + `pytest`
3. **build** — Matrix build across Linux, macOS, Windows for multiple Python versions

To add automated PyPI publishing on tag, add a release job:

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ["v*"]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: PyO3/maturin-action@v1
        with:
          command: publish
          args: --skip-existing
        env:
          MATURIN_PYPI_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
```

---

## Verify the Build

```python
import pyratatui
print(pyratatui.__version__)           # e.g. "0.1.0"
print(pyratatui.__ratatui_version__)   # "0.29"

# Sanity check: run a no-display render
from pyratatui import Buffer, Rect, Paragraph, Text

buf  = Buffer(Rect(0, 0, 40, 5))
# (widgets write into buf in tests via ratatui's stateless render)
print("Build OK")
```

---

## Web App (WASM) Build

The `pyratatui.ratxilla` module is pure Python — **no WASM build required**. For reference, the legacy WASM approach was:
[trunk](https://trunkrs.dev), not Maturin.

### Prerequisites

```bash
# Install trunk (builds and serves WASM apps)
cargo install --locked trunk

# Add the wasm32 target
rustup target add wasm32-unknown-unknown
```

### Build

```bash
./scripts/build_web.sh            # debug build
./scripts/build_web.sh --release  # release (smaller, optimised WASM)
# Output: pyratatui.ratxilla (pure-Python, no WASM needed)dist/
```

### Serve the WASM bundle

```bash
# Quick test
python -m http.server 8080 --directory pyratatui.ratxilla (pure-Python, no WASM needed)dist/
# Open http://localhost:8080/

# Or use the pyratatui.web Python server which auto-serves dist/
python examples/26_web_counter.py
```

### Directory layout after build

```
pyratatui.ratxilla (pure-Python, no WASM needed)
├── dist/
│   ├── index.html              # bundled page
├── src/main.rs
├── Cargo.toml
└── index.html                  # trunk source template
```
