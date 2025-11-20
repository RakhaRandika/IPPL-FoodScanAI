<#
Setup script for TensorFlow-compatible virtual environment on Windows PowerShell.
Usage:
  1) Ensure you have Python 3.11 installed and on PATH as 'python' or provide full path.
  2) Run: .\setup_tf_env.ps1 -PythonExe 'C:\Path\to\python.exe'

This script will:
  - Create a venv in .venv_tf (to avoid clobbering existing venv)
  - Activate venv and upgrade pip
  - Install tensorflow-cpu and backend requirements
#>

param(
    [string]$PythonExe = "python"
)

Write-Host "Using Python executable: $PythonExe"

try {
    $pyVersion = & $PythonExe -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>&1
} catch {
    Write-Error "Failed to invoke Python at path: $PythonExe. Please install Python 3.11 and retry or provide correct path."
    exit 1
}

Write-Host "Detected Python version: $pyVersion"

if ($pyVersion -notmatch '^3\.11') {
    Write-Warning "TensorFlow (recommended) supports Python 3.11 or 3.10. Detected: $pyVersion. Consider installing Python 3.11. Continuing may fail."
}

$venvPath = Join-Path -Path $PSScriptRoot -ChildPath '.venv_tf'
if (-Not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at: $venvPath"
    & $PythonExe -m venv $venvPath
}

$activate = Join-Path -Path $venvPath -ChildPath 'Scripts\Activate.ps1'
Write-Host "Activating venv: $venvPath"
& $activate

Write-Host "Upgrading pip and installing dependencies..."
pip install --upgrade pip

# Minimal backend requirements; add more as needed
pip install tensorflow-cpu pillow numpy fastapi uvicorn python-multipart httpx python-dotenv

Write-Host "Installation complete. To activate the venv later run:`n  & '$activate'"
Write-Host "Run the FastAPI server (from backend folder):`n  uvicorn app.main:app --reload --port 8000"
