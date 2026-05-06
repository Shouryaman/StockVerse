# Runs stock_picker with this project virtualenv.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$crewai = Join-Path $PSScriptRoot '.venv\Scripts\crewai.exe'
if (-not (Test-Path $crewai)) {
  Write-Error "Missing .venv\Scripts\crewai.exe. Run 'uv sync' first."
}
& $crewai run @args
