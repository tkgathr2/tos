param(
  [string]$Root = "C:\Users\takag\00_dev\tos"
)

$ErrorActionPreference = "Stop"

Write-Host "TOS cc_run start"
Write-Host "Root: $Root"

# 1) init
$initPath = Join-Path $Root "tools\init.ps1"
if (-not (Test-Path $initPath)) {
  Write-Host "init.ps1 not found: $initPath"
  exit 1
}

powershell -NoProfile -ExecutionPolicy Bypass -File $initPath
if ($LASTEXITCODE -ne 0) {
  Write-Host "init failed with exit code: $LASTEXITCODE"
  exit $LASTEXITCODE
}

# 2) run orchestrator
$orch = Join-Path $Root "orchestrator_v0_3.py"
if (-not (Test-Path $orch)) {
  Write-Host "orchestrator_v0_3.py not found: $orch"
  exit 1
}

$pyPathFile = Join-Path $Root "tos_python_path.txt"
if (-not (Test-Path $pyPathFile)) {
  Write-Host "tos_python_path.txt not found: $pyPathFile"
  exit 1
}

$py = (Get-Content $pyPathFile -Encoding UTF8 | Select-Object -First 1).Trim()
if (-not (Test-Path $py)) {
  Write-Host "python path invalid: $py"
  exit 1
}

Write-Host "Python: $py"
& $py $orch
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
  Write-Host "orchestrator failed with exit code: $exitCode"
  exit $exitCode
}

Write-Host "TOS cc_run end"
exit 0
