param(
  [string]$Root = "C:\Users\takag\00_dev\tos"
)

$ErrorActionPreference = "Stop"

Write-Host "TOS cc_run start"
Write-Host "Root: $Root"

# 1) init
$initPath = Join-Path $Root "tools\init.ps1"
if (-not (Test-Path $initPath)) {
  throw "init.ps1 not found: $initPath"
}

powershell -NoProfile -ExecutionPolicy Bypass -File $initPath

# 2) run orchestrator
$orch = Join-Path $Root "orchestrator_v0_3.py"
if (-not (Test-Path $orch)) {
  throw "orchestrator_v0_3.py not found: $orch"
}

$pyPathFile = Join-Path $Root "tos_python_path.txt"
if (-not (Test-Path $pyPathFile)) {
  throw "tos_python_path.txt not found: $pyPathFile"
}

$py = (Get-Content $pyPathFile -Encoding UTF8 | Select-Object -First 1).Trim()
if (-not (Test-Path $py)) {
  throw "python path invalid: $py"
}

Write-Host "Python: $py"
& $py $orch

Write-Host "TOS cc_run end"
