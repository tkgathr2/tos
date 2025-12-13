param(
  [string]$Root = "C:\Users\takag\00_dev\tos"
)

$ErrorActionPreference = "Stop"

Write-Host "TOS init start"
Write-Host "Root: $Root"

if (-not (Test-Path $Root)) {
  New-Item -ItemType Directory -Path $Root -Force | Out-Null
  Write-Host "Created root directory"
}

$dirs = @(
  (Join-Path $Root "workspace\generated"),
  (Join-Path $Root "workspace\results"),
  (Join-Path $Root "workspace\artifacts"),
  (Join-Path $Root "logs\steps"),
  (Join-Path $Root "tools")
)

foreach ($d in $dirs) {
  if (-not (Test-Path $d)) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
    Write-Host "Created dir: $d"
  }
}

$mustFiles = @(
  (Join-Path $Root "config_v0_3.json"),
  (Join-Path $Root "orchestrator_v0_3.py"),
  (Join-Path $Root "tos_python_path.txt")
)

foreach ($f in $mustFiles) {
  if (Test-Path $f) {
    Write-Host "Found file: $f"
  } else {
    Write-Host "Missing file: $f"
  }
}

$pyCandidates = @()
try {
  $pyCandidates = (where.exe python 2>$null)
} catch {
  $pyCandidates = @()
}

if ($pyCandidates.Count -gt 0) {
  Write-Host "where python results:"
  $pyCandidates | ForEach-Object { Write-Host "  $_" }
} else {
  Write-Host "where python returned nothing"
}

$tosPyPathFile = Join-Path $Root "tos_python_path.txt"
if (Test-Path $tosPyPathFile) {
  $tosPy = (Get-Content $tosPyPathFile -ErrorAction Stop | Select-Object -First 1).Trim()
  Write-Host "tos_python_path.txt: $tosPy"
  if ($tosPy -and (Test-Path $tosPy)) {
    $ver = & $tosPy --version 2>&1
    Write-Host "tos python version: $ver"
  } else {
    Write-Host "tos python path is missing or invalid"
  }
} else {
  Write-Host "tos_python_path.txt not found"
}

# API key check
$missingKeys = @()
if (-not $env:OPENAI_API_KEY) {
  $missingKeys += "OPENAI_API_KEY"
}
if (-not $env:ANTHROPIC_API_KEY) {
  $missingKeys += "ANTHROPIC_API_KEY"
}

if ($missingKeys.Count -gt 0) {
  Write-Host ""
  Write-Host "Missing required environment variables:"
  foreach ($key in $missingKeys) {
    Write-Host "  $key"
  }
  exit 1
}

Write-Host "API keys OK"
Write-Host "TOS init done"
