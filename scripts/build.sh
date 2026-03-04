#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

OS="$(uname -s)"
ARCH="$(uname -m)"

echo "🐀 pyratatui build script"
echo "   OS:   $OS"
echo "   Arch: $ARCH"

command -v maturin >/dev/null || { echo "maturin not found"; exit 1; }
command -v cargo >/dev/null || { echo "cargo not found"; exit 1; }

echo "✅  $(maturin --version)"
echo "✅  $(cargo --version)"

MODE="${1:-}"

case "$MODE" in
    --dev)
        echo "🔧 Development mode..."
        maturin develop --release
        echo "✅  Installed (editable)."
        ;;
    --sdist)
        echo "📦 Building sdist..."
        maturin sdist --out dist/
        echo "✅  sdist created."
        ;;
    *)
        echo "📦 Building release wheel..."
        maturin build --release --strip --out dist/

        WHEEL="$(ls -t dist/*.whl 2>/dev/null | head -n 1 || true)"

        if [[ -z "$WHEEL" ]]; then
            echo "No wheel produced."
            exit 1
        fi

        echo "🚀 Installing $(basename "$WHEEL")..."
        pip install --upgrade "$WHEEL" --force-reinstall

        echo "✅  Installed successfully."
        ;;
esac
