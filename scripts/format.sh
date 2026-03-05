#!/usr/bin/env bash
set -e

echo "Installing/updating Python formatters..."
python -m pip install --upgrade pip
python -m pip install --upgrade ruff black isort

# Optional: setup isort config
# echo -e "[tool.isort]\nprofile = \"black\"" > pyproject.toml

echo "Running Ruff format..."
ruff format . --exit-zero

echo "Running isort..."
python -m isort .

echo "Running Black..."
python -m black .

# Run Rust formatter
if command -v cargo &> /dev/null
then
    echo "Running cargo fmt..."
    cargo fmt
else
    echo "Cargo not found. Skipping Rust formatting."
fi

echo "Formatting complete."
