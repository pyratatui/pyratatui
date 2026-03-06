param(
    [string]$Mode = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
Set-Location $ProjectDir

Write-Host "[pyratatui] build script (Windows)" -ForegroundColor Cyan
Write-Host "   OS:   Windows"
Write-Host "   Arch: $env:PROCESSOR_ARCHITECTURE"

if (-not (Get-Command maturin -ErrorAction SilentlyContinue)) {
    Write-Error "maturin not found. Install with: pip install maturin"
    exit 1
}

if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Error "cargo not found. Install Rust: https://rustup.rs"
    exit 1
}

Write-Host "[OK] $(maturin --version)"
Write-Host "[OK] $(cargo --version)"

switch ($Mode) {
    "--dev" {
        Write-Host "`n[DEV] Development mode (editable install)..."
        maturin develop --release
        Write-Host "[OK] Installed (editable)."
    }
    "--sdist" {
        Write-Host "`n[SDIST] Building source distribution..."
        maturin sdist --out dist\
        Write-Host "[OK] sdist created in dist\"
    }
    default {
        Write-Host "`n[BUILD] Building release wheel..."
        maturin build --release --strip --out dist\

        $wheel = Get-ChildItem dist\*.whl |
                 Sort-Object LastWriteTime -Descending |
                 Select-Object -First 1

        if (-not $wheel) {
            Write-Error "No wheel produced in dist\"
            exit 1
        }

        Write-Host "[INSTALL] Installing $($wheel.Name)..."
        pip install --upgrade $wheel.FullName --force-reinstall

        Write-Host "[OK] Installed successfully."
    }
}
