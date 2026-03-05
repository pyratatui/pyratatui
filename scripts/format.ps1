# Install/update Python formatters
Write-Host "Installing/updating Python formatters..."
python -m pip install --upgrade pip
python -m pip install --upgrade ruff black isort

# Optional: setup isort config
# Set-Content -Path .\pyproject.toml -Value "[tool.isort]`nprofile = 'black'"

# Run Python formatters
Write-Host "Running Ruff format..."
ruff format . --exit-zero

Write-Host "Running isort..."
python -m isort .

Write-Host "Running Black..."
python -m black .

# Run Rust formatter
if (Get-Command cargo -ErrorAction SilentlyContinue) {
    Write-Host "Running cargo fmt..."
    cargo fmt
} else {
    Write-Warning "Cargo not found. Skipping Rust formatting."
}

Write-Host "Formatting complete."
