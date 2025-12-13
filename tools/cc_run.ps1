param(
  [string]$Root = "C:\Users\takag\00_dev\tos",
  [ValidateSet("run", "test", "cleanrun")]
  [string]$Mode = "run",
  [switch]$Clean
)

$ErrorActionPreference = "Stop"

Write-Host "TOS cc_run start"
Write-Host "Root: $Root"
Write-Host "Mode: $Mode"

# cleanrun mode enables Clean internally
if ($Mode -eq "cleanrun") {
  $Clean = $true
}

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

# 3) test mode: verify exit code and log files
if ($Mode -eq "test") {
  Write-Host ""
  Write-Host "=== Test Mode Verification ==="

  $testPassed = $true

  # Check exit code
  if ($exitCode -ne 0) {
    Write-Host "FAIL: orchestrator exit code = $exitCode"
    $testPassed = $false
  } else {
    Write-Host "OK: orchestrator exit code = 0"
  }

  # Check phase_state.json
  $phaseState = Join-Path $Root "workspace\artifacts\phase_state.json"
  if (Test-Path $phaseState) {
    Write-Host "OK: phase_state.json exists"
  } else {
    Write-Host "FAIL: phase_state.json not found"
    $testPassed = $false
  }

  # Check step files
  $stepsDir = Join-Path $Root "logs\steps"
  $stepFiles = Get-ChildItem -Path $stepsDir -Filter "step_*.json" -ErrorAction SilentlyContinue
  if ($stepFiles.Count -gt 0) {
    Write-Host "OK: step files exist (count=$($stepFiles.Count))"
  } else {
    Write-Host "FAIL: no step files found"
    $testPassed = $false
  }

  # Check phase_summary.json
  $phaseSummary = Join-Path $Root "logs\phase_summary.json"
  if (Test-Path $phaseSummary) {
    Write-Host "OK: phase_summary.json exists"
  } else {
    Write-Host "FAIL: phase_summary.json not found"
    $testPassed = $false
  }

  Write-Host ""
  if ($testPassed) {
    Write-Host "Test PASSED"
    exit 0
  } else {
    Write-Host "Test FAILED"
    exit 1
  }
}

# Normal exit for run/cleanrun modes
if ($exitCode -ne 0) {
  Write-Host "orchestrator failed with exit code: $exitCode"
  exit $exitCode
}

# 4) summary display
$phaseState = Join-Path $Root "workspace\artifacts\phase_state.json"
if (Test-Path $phaseState) {
  $state = Get-Content $phaseState -Encoding UTF8 | ConvertFrom-Json
  Write-Host "phase_state phase=$($state.current_phase) step=$($state.current_step) done=$($state.last_done)"
} else {
  Write-Host "phase_state none"
}

$stepsDir = Join-Path $Root "logs\steps"
$stepFiles = Get-ChildItem -Path $stepsDir -Filter "step_*.json" -ErrorAction SilentlyContinue | Sort-Object Name -Descending
if ($stepFiles.Count -gt 0) {
  $latestStep = $stepFiles[0].Name
  Write-Host "latest_step $latestStep total=$($stepFiles.Count)"
} else {
  Write-Host "latest_step none"
}

$phaseSummary = Join-Path $Root "logs\phase_summary.json"
if (Test-Path $phaseSummary) {
  Write-Host "phase_summary exists"
} else {
  Write-Host "phase_summary none"
}

Write-Host "TOS cc_run end"
exit 0
