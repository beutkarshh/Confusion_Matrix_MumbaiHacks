<#
Start both backend (FastAPI/uvicorn) and frontend (Vite React) for local dev on Windows PowerShell.

Behavior:
- Ensures we're at repo root (relative to this script)
- Creates/uses .venv, installs backend requirements
- Starts backend on http://127.0.0.1:8000 with reload
- Installs frontend packages if needed and starts Vite on http://localhost:8080
- Opens each in its own PowerShell window to see logs
#>

$ErrorActionPreference = 'Stop'

# Resolve repo root based on script location
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "Project root:" $root -ForegroundColor Cyan

# Ensure PYTHONPATH for backend imports
$env:PYTHONPATH = $root

# Ensure virtualenv exists
if (-not (Test-Path "$root\.venv\Scripts\python.exe")) {
	Write-Host "Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
	python -m venv .venv
}

# Upgrade pip and install backend requirements
Write-Host "Installing backend requirements..." -ForegroundColor Yellow
& "$root\.venv\Scripts\python.exe" -m pip install --upgrade pip | Out-Host
& "$root\.venv\Scripts\python.exe" -m pip install -r "$root\requirements.txt" | Out-Host

# Start backend in a new PowerShell window
Write-Host "Starting backend (uvicorn) on http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process -FilePath "powershell.exe" -ArgumentList @(
	'-NoExit',
	'-Command',
	"`$env:PYTHONPATH='$root'; & '$root\.venv\Scripts\python.exe' -m uvicorn server.main:app --host 127.0.0.1 --port 8000 --reload"
)

# Install frontend deps and start Vite in another window
$frontend = Join-Path $root 'frontend'
if (-not (Test-Path $frontend)) {
	Write-Error "Frontend folder not found at: $frontend"
	exit 1
}

Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -WorkingDirectory $frontend -ArgumentList @(
	'-NoExit',
	'-Command',
	'npm install; npm run dev'
)

Write-Host "Both servers are launching:" -ForegroundColor Cyan
Write-Host " - Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host " - Frontend: http://localhost:8080" -ForegroundColor Cyan
