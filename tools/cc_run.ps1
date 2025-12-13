param(
  [string]$Root = "C:\Users\takag\00_dev\tos",
  [string]$Mode,
  [switch]$Clean,
  [string]$SummaryFile
)

$ErrorActionPreference = "Stop"

function Show-Usage {
  Write-Host "usage cc_run.ps1 -Mode run|test|cleanrun -Clean -SummaryFile path"
}

# Check -Mode is specified
if (-not $PSBoundParameters.ContainsKey('Mode')) {
  Show-Usage
  exit 1
}

# Check -Mode is valid
if ($Mode -notin @("run", "test", "cleanrun")) {
  Show-Usage
  exit 1
}

Write-Host "TOS cc_run start"
Write-Host "Root $Root"
Write-Host "Mode $Mode"

# cleanrun mode enables Clean internally
if ($Mode -eq "cleanrun") {
  $Clean = $true
}

# 0) optional cleanup (runs once even if both -Clean and cleanrun)
if ($Clean) {
  Write-Host "cleanup start"
  $stepsDir = Join-Path $Root "logs\steps"
  $phaseSummary = Join-Path $Root "logs\phase_summary.json"
  $phaseState = Join-Path $Root "workspace\artifacts\phase_state.json"

  if (Test-Path $stepsDir) {
    Get-ChildItem -Path $stepsDir -Filter "step_*.json" | Remove-Item -Force
  }
  if (Test-Path $phaseSummary) {
    Remove-Item -Path $phaseSummary -Force
  }
  if (Test-Path $phaseState) {
    Remove-Item -Path $phaseState -Force
  }
  Write-Host "cleanup done"
}

# 1) init
$initPath = Join-Path $Root "tools\init.ps1"
if (-not (Test-Path $initPath)) {
  Write-Host "init.ps1 not found $initPath"
  exit 1
}

powershell -NoProfile -ExecutionPolicy Bypass -File $initPath
$initExitCode = $LASTEXITCODE
if ($initExitCode -ne 0) {
  Write-Host "init failed with exit code $initExitCode"
  exit $initExitCode
}

# 2) run orchestrator
$orch = Join-Path $Root "orchestrator_v0_3.py"
if (-not (Test-Path $orch)) {
  Write-Host "orchestrator_v0_3.py not found $orch"
  exit 1
}

$pyPathFile = Join-Path $Root "tos_python_path.txt"
if (-not (Test-Path $pyPathFile)) {
  Write-Host "tos_python_path.txt not found $pyPathFile"
  exit 1
}

$py = (Get-Content $pyPathFile -Encoding UTF8 | Select-Object -First 1).Trim()
if (-not (Test-Path $py)) {
  Write-Host "python path invalid $py"
  exit 1
}

Write-Host "Python $py"
& $py $orch
$orchExitCode = $LASTEXITCODE

# Helper function to save summary
function Save-Summary {
  param([string]$FilePath)

  $summary = @{
    phase = $null
    step = $null
    done = $null
    latest_step = $null
    step_count = 0
    phase_summary_exists = $false
  }

  $phaseStatePath = Join-Path $Root "workspace\artifacts\phase_state.json"
  if (Test-Path $phaseStatePath) {
    $state = Get-Content $phaseStatePath -Encoding UTF8 | ConvertFrom-Json
    $summary.phase = $state.current_phase
    $summary.step = $state.current_step
    $summary.done = $state.last_done
  }

  $stepsDir = Join-Path $Root "logs\steps"
  $stepFiles = Get-ChildItem -Path $stepsDir -Filter "step_*.json" -ErrorAction SilentlyContinue | Sort-Object Name -Descending
  if ($stepFiles.Count -gt 0) {
    $summary.latest_step = $stepFiles[0].Name
    $summary.step_count = $stepFiles.Count
  }

  $phaseSummaryPath = Join-Path $Root "logs\phase_summary.json"
  if (Test-Path $phaseSummaryPath) {
    $summary.phase_summary_exists = $true
  }

  $fullPath = Join-Path $Root $FilePath
  $summary | ConvertTo-Json -Depth 10 | Set-Content -Path $fullPath -Encoding UTF8
  Write-Host "summary saved $fullPath"
}

# 3) test mode: verify exit code and log files
if ($Mode -eq "test") {
  $testPassed = $true

  # Check init exit code
  if ($initExitCode -ne 0) {
    Write-Host "FAIL init exit code = $initExitCode"
    $testPassed = $false
  }

  # Check orchestrator exit code
  if ($orchExitCode -ne 0) {
    Write-Host "FAIL orchestrator exit code = $orchExitCode"
    $testPassed = $false
  }

  # Check tos_python_path.txt
  $pyPathFile = Join-Path $Root "tos_python_path.txt"
  if (-not (Test-Path $pyPathFile)) {
    Write-Host "FAIL tos_python_path.txt not found"
    $testPassed = $false
  }

  # Check phase_state.json
  $phaseState = Join-Path $Root "workspace\artifacts\phase_state.json"
  if (-not (Test-Path $phaseState)) {
    Write-Host "FAIL phase_state.json not found"
    $testPassed = $false
  }

  # Check step files
  $stepsDir = Join-Path $Root "logs\steps"
  $stepFiles = Get-ChildItem -Path $stepsDir -Filter "step_*.json" -ErrorAction SilentlyContinue
  if ($stepFiles.Count -eq 0) {
    Write-Host "FAIL no step files found"
    $testPassed = $false
  }

  # Save summary if specified
  if ($SummaryFile) {
    Save-Summary -FilePath $SummaryFile
  }

  if ($testPassed) {
    Write-Host "test passed"
    exit 0
  } else {
    Write-Host "test failed"
    exit 1
  }
}

# Normal exit for run/cleanrun modes
if ($orchExitCode -ne 0) {
  Write-Host "orchestrator failed with exit code $orchExitCode"
  exit $orchExitCode
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

# Save summary if specified
if ($SummaryFile) {
  Save-Summary -FilePath $SummaryFile
}

Write-Host "TOS cc_run end"
exit 0
