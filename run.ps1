# Run Dumroo Admin Streamlit app via venv with safe activation
param(
  [int]$Port = 8501
)
$ErrorActionPreference = 'Stop'
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force | Out-Null
if (-not (Test-Path ".venv/Scripts/Activate.ps1")) {
  Write-Host "Creating virtual environment..." -ForegroundColor Cyan
  python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$streamlit = Join-Path (Resolve-Path ".venv/Scripts").Path "streamlit.exe"
& $streamlit run src/app.py --server.port $Port
