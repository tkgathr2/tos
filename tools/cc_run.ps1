param(
  [string]$Root = "C:\Users\takag\00_dev\tos",
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

Write-Host "TOS cc_run start"
Write-Host "Root: $Root"

# 0) optional cleanup
if ($Clean) {
  Write-Host "Cleanup enabled"
  $stepsDir = Join-Path $Root "logs\steps"
  $phaseSummary = Join-Path $Root "logs\phase_summary.json"
  $phaseState = Join-Path $Root "workspace\artifacts\phase_state.json"

  if (Test-Path $stepsDir) {
    Get-ChildItem -Path $stepsDir -Filter "step_*.json" | Remove-Item -Force
    Write-Host "Cleaned: logs/steps/step_*.json"
  }
  if (Test-Path $phaseSummary) {
    Remove-Item -Path $phaseSummary -Force
    Write-Host "Cleaned: logs/phase_summary.json"
  }
  if (Test-Path $phaseState) {
    Remove-Item -Path $phaseState -Force
    Write-Host "Cleaned: workspace/artifacts/phase_state.json"
  }
}

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
