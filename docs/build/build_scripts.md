# CI & Release System

pyratatui uses a **manual release pipeline** powered by
GitHub Actions.

Releases are deterministic and versioned directly from `Cargo.toml`.

There are **no tag-triggered builds** and no manual version input.

The version source of truth is:

```toml
[package]
version = "0.3.1"
```

The workflow reads this value using `cargo metadata` and uses it for:

* GitHub Release tag (`v0.3.1`)
* Wheel filenames
* PyPI publish
* SHA256 checksum file

One source. Zero drift.

---

# Release Flow

## Step 1 — Bump Version

Edit `Cargo.toml`:

```toml
version = "0.3.2"
```

Commit and push.

## Step 2 — Run CI Manually

Go to:

```
GitHub → Actions → CI → Run workflow
```

That’s it.

The workflow will:

1. Run Rust lint + tests
2. Run Python lint + tests
3. Build wheels (Linux, macOS, Windows)
4. Generate `SHA256SUMS`
5. Create a GitHub Release:

   ```
   v0.3.2
   ```
6. Upload:

   * All `.whl` files
   * `SHA256SUMS`
7. Publish to PyPI

No tagging required.
No manual version entry.
No duplication.

---

# GitHub Release Artifacts

Each release contains:

* `*.whl` files (per OS/arch)
* `SHA256SUMS`

Users can verify integrity:

```bash
sha256sum -c SHA256SUMS
```

This ensures supply-chain integrity and reproducibility.

---

# Cross-Platform Wheel Matrix

| Platform          | Arch    | Python       | Built By       |
| ----------------- | ------- | ------------ | -------------- |
| Linux (manylinux) | x86_64  | 3.10+ (ABI3) | ubuntu-latest  |
| macOS             | x86_64  | 3.10+ (ABI3) | macos-latest   |
| macOS             | aarch64 | 3.10+ (ABI3) | macos-latest   |
| Windows           | x86_64  | 3.10+ (ABI3) | windows-latest |

Because wheels use ABI3, a single build per OS/arch supports Python 3.10+.

---

# Build Scripts

## `scripts/build.sh` (Linux / macOS)

```bash
./scripts/build.sh          # Release wheel → dist/
./scripts/build.sh --dev    # Editable install in current venv
./scripts/build.sh --sdist  # Source distribution
```

Requirements:

* Rust stable
* maturin

Install:

```bash
rustup install stable
pip install maturin
```

---

## `scripts/build.ps1` (Windows)

```powershell
.\scripts\build.ps1
.\scripts\build.ps1 --dev
.\scripts\build.ps1 --sdist
```

---

# Development Shortcut

Fastest local loop:

```bash
pip install maturin
maturin develop --release
```

This compiles Rust and installs the extension into the active venv in-place.

---

# Packaging Details

## ABI3 Wheels

pyratatui ships ABI3-compatible wheels.

Relevant `pyproject.toml` section:

```toml
[tool.maturin]
python-source = "python"
module-name = "pyratatui._pyratatui"
bindings = "pyo3"
features = ["pyo3/extension-module"]
```

ABI3 ensures compatibility with Python 3.10+ without rebuilding per minor version.

---

## Type Information

The wheel includes:

* `pyratatui/__init__.pyi`
* `py.typed`

This ensures full PEP 561 compliance and proper IDE support.

---

# Publishing Model

Publishing is fully automated via the CI workflow.

Manual steps like `twine upload` are not required.

The pipeline:

1. Builds wheels
2. Creates GitHub Release
3. Publishes to PyPI

Only after tests pass.

---

# Versioning

pyratatui follows Semantic Versioning:

* MAJOR → breaking changes
* MINOR → new features
* PATCH → fixes

There is no tag-based release trigger.

The canonical version lives in `Cargo.toml`.

---
