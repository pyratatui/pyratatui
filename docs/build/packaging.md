# Packaging & Distribution

This guide covers publishing pyratatui wheels to PyPI and distributing to end users.

---

## Project Structure

```
pyratatui/
├── Cargo.toml          # Rust package manifest
├── pyproject.toml      # Python package metadata + Maturin config
├── src/                # Rust source (PyO3 bindings)
├── python/
│   └── pyratatui/
│       ├── __init__.py       # Python re-exports
│       ├── __init__.pyi      # Type stubs
│       ├── async_terminal.py # AsyncTerminal implementation
│       └── helpers.py        # run_app / run_app_async
└── tests/
```

---

## `pyproject.toml` Overview

```toml
[build-system]
requires = ["maturin>=1.4,<2.0"]
build-backend = "maturin"

[project]
name = "pyratatui"
requires-python = ">=3.10"
classifiers = [
    "Programming Language :: Rust",
    "Programming Language :: Python :: Implementation :: CPython",
    "Environment :: Console",
    "Topic :: Terminals",
]

[tool.maturin]
python-source = "python"       # Python package lives here
features = ["pyo3/extension-module"]
module-name = "pyratatui._pyratatui"
```

The `module-name` setting ensures the compiled `.so` / `.pyd` is placed as `pyratatui/_pyratatui.so`, which the package's `__init__.py` imports from.

---

## Version Bumping

pyratatui uses the version from `Cargo.toml`:

```toml
[package]
name = "pyratatui"
version = "0.2.0"
```

Maturin automatically syncs this to the Python package version. Always bump `Cargo.toml` before releasing.

---

## Manual PyPI Upload

```bash
# Build all wheels for current platform
maturin build --release --strip

# Upload to PyPI (requires twine or maturin publish)
pip install twine
twine upload target/wheels/*.whl

# Or use maturin publish directly
maturin publish
```

`maturin publish` requires `MATURIN_PYPI_TOKEN` set to a valid PyPI API token.

---

## Multi-Platform Wheel Matrix

For a complete PyPI release, build wheels on each platform:

| Platform | Architecture | Command |
|---|---|---|
| Linux | x86_64 (manylinux) | `docker` + maturin action |
| Linux | aarch64 (manylinux) | `docker` + `--zig` |
| macOS | universal2 | `--target universal2-apple-darwin` |
| Windows | x86_64 | `maturin build --release` |

The GitHub Actions workflow at `.github/workflows/gendocs.yml` demonstrates the matrix strategy.

---

## Wheel Naming Convention

Maturin produces wheels with names like:

```
pyratatui-0.2.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

Breakdown:

| Segment | Meaning |
|---|---|
| `pyratatui-0.2.0` | Package name and version |
| `cp311-cp311` | CPython 3.11 (ABI tag) |
| `manylinux_2_17_x86_64` | Linux platform tag |

Pure-Python fallback wheels are not produced — the extension module is always required.

---

## Installing in Restricted Environments

If your environment cannot compile from source:

```bash
# Download wheel file and install offline
pip download pyratatui --no-deps -d ./wheels/
pip install --no-index --find-links=./wheels/ pyratatui
```

Or pre-build a wheel on a matching system and distribute it via an internal package index.

---

## Type Stubs Distribution

The `python/pyratatui/__init__.pyi` file is included automatically by Maturin as part of the wheel. IDEs (PyCharm, VS Code with Pylance) and type checkers (mypy, pyright) will discover it automatically.

To verify stubs are present in an installed wheel:

```bash
python -c "import pyratatui; import pathlib; \
  p = pathlib.Path(pyratatui.__file__).parent; \
  print(list(p.glob('*.pyi')))"
```

---

## Minimum Supported Python

The `requires-python = ">=3.10"` constraint in `pyproject.toml` is enforced by pip at install time. The PyO3 `Bound<>` API used in the Rust source requires PyO3 0.22+, which supports Python 3.8+, but the Python source uses 3.10-only syntax (structural pattern matching not currently used, but `match`/`case` readiness is assumed for downstream code).
