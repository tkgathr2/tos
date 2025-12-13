param(
  [string]$Root = "C:\Users\takag\00_dev\tos",
  [string]$Mode,
  [switch]$Clean,
  [string]$SummaryFile,
  [string]$CheckpointName,
  [string]$TargetCommit
)

$ErrorActionPreference = "Stop"

# EE: Updated usage
function Show-Usage {
  Write-Host "usage cc_run.ps1 -Mode run|test|cleanrun|checkpoint|rollback -Clean -SummaryFile path"
  Write-Host "  checkpoint: -CheckpointName <text>"
  Write-Host "  rollback: -TargetCommit <hash> (optional, uses last_checkpoint.txt if not specified)"
}

# Check -Mode is specified
if (-not $PSBoundParameters.ContainsKey('Mode')) {
  Show-Usage
  exit 1
}

# Check -Mode is valid
if ($Mode -notin @("run", "test", "cleanrun", "checkpoint", "rollback")) {
  Show-Usage
  exit 1
}

Write-Host "TOS cc_run start"
Write-Host "Root $Root"
Write-Host "Mode $Mode"

# EC: checkpoint mode
if ($Mode -eq "checkpoint") {
  if (-not $CheckpointName) {
    Write-Host "error: -CheckpointName required for checkpoint mode"
    Show-Usage
    exit 1
  }

  $checkpointScript = Join-Path $Root "tools\checkpoint.ps1"
  if (-not (Test-Path $checkpointScript)) {
    Write-Host "checkpoint.ps1 not found $checkpointScript"
    exit 1
  }

  powershell -NoProfile -ExecutionPolicy Bypass -File $checkpointScript -Root $Root -Name $CheckpointName
  $cpExitCode = $LASTEXITCODE

  if ($cpExitCode -ne 0) {
    Write-Host "checkpoint failed with exit code $cpExitCode"
    exit $cpExitCode
  }

  # EJ: Save commit hash to last_checkpoint.txt
  $hash = git -C $Root rev-parse HEAD
  $lastCheckpointFile = Join-Path $Root "logs\last_checkpoint.txt"
  $hash | Set-Content -Path $lastCheckpointFile -Encoding UTF8
  Write-Host "last_checkpoint saved $lastCheckpointFile"

  # EP: checkpoint output
  Write-Host "checkpoint $hash"

  # EO/FG/GQ: Save summary with checkpoint_hash (JSON and TXT)
  if ($SummaryFile) {
    if ([System.IO.Path]::IsPathRooted($SummaryFile)) {
      $fullPath = $SummaryFile
    } else {
      $fullPath = Join-Path $Root $SummaryFile
    }
    # GQ: Add timestamp and root
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    $summary = @{
      mode = "checkpoint"
      checkpoint_hash = $hash
      timestamp = $timestamp
      root = $Root
    }
    $summary | ConvertTo-Json -Depth 10 | Set-Content -Path $fullPath -Encoding UTF8
    # FG: Save TXT
    $txtPath = [System.IO.Path]::ChangeExtension($fullPath, ".txt")
    $txtContent = "mode=checkpoint checkpoint_hash=$hash timestamp=$timestamp root=$Root"
    $txtContent | Set-Content -Path $txtPath -Encoding UTF8
    Write-Host "summary saved $fullPath"
  }

  # FM: Summary display
  Write-Host "TOS cc_run end"
  exit 0
}

# ED: rollback mode
if ($Mode -eq "rollback") {
  # ER: Check for dirty working tree before rollback
  $gitStatus = git -C $Root status --porcelain
  if ($gitStatus) {
    Write-Host "error: working tree is dirty, commit or stash changes first"
    Write-Host $gitStatus
    exit 1
  }

  # EL: If TargetCommit not specified, use last_checkpoint.txt
  if (-not $TargetCommit) {
    $lastCheckpointFile = Join-Path $Root "logs\last_checkpoint.txt"
    if (Test-Path $lastCheckpointFile) {
      $TargetCommit = (Get-Content $lastCheckpointFile -Encoding UTF8 | Select-Object -First 1).Trim()
      Write-Host "using last_checkpoint $TargetCommit"
    } else {
      Write-Host "error: -TargetCommit required (no last_checkpoint.txt found)"
      Show-Usage
      exit 1
    }
  }

  $rollbackScript = Join-Path $Root "tools\rollback.ps1"
  if (-not (Test-Path $rollbackScript)) {
    Write-Host "rollback.ps1 not found $rollbackScript"
    exit 1
  }

  powershell -NoProfile -ExecutionPolicy Bypass -File $rollbackScript -Root $Root -TargetCommit $TargetCommit
  $rbExitCode = $LASTEXITCODE

  if ($rbExitCode -ne 0) {
    Write-Host "rollback failed with exit code $rbExitCode"
    exit $rbExitCode
  }

  # EQ: rollback output
  Write-Host "rollback $TargetCommit"

  # EO/FG/GQ: Save summary with rollback_target (JSON and TXT)
  if ($SummaryFile) {
    if ([System.IO.Path]::IsPathRooted($SummaryFile)) {
      $fullPath = $SummaryFile
    } else {
      $fullPath = Join-Path $Root $SummaryFile
    }
    # GQ: Add timestamp and root
    $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    $summary = @{
      mode = "rollback"
      rollback_target = $TargetCommit
      timestamp = $timestamp
      root = $Root
    }
    $summary | ConvertTo-Json -Depth 10 | Set-Content -Path $fullPath -Encoding UTF8
    # FG: Save TXT
    $txtPath = [System.IO.Path]::ChangeExtension($fullPath, ".txt")
    $txtContent = "mode=rollback rollback_target=$TargetCommit timestamp=$timestamp root=$Root"
    $txtContent | Set-Content -Path $txtPath -Encoding UTF8
    Write-Host "summary saved $fullPath"
  }

  # EM/GO/GP: Auto run test after rollback with -Clean and optional SummaryFile
  Write-Host "auto test after rollback"
  $ccRunScript = Join-Path $Root "tools\cc_run.ps1"
  $testArgs = @("-Root", $Root, "-Mode", "test", "-Clean")
  if ($SummaryFile) {
    $testArgs += @("-SummaryFile", $SummaryFile)
  }
  powershell -NoProfile -ExecutionPolicy Bypass -File $ccRunScript @testArgs
  $testExitCode = $LASTEXITCODE

  if ($testExitCode -ne 0) {
    Write-Host "test after rollback failed"
    exit 1
  }

  Write-Host "TOS cc_run end"
  exit 0
}

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

  # Resolve path: absolute or relative to Root
  if ([System.IO.Path]::IsPathRooted($FilePath)) {
    $fullPath = $FilePath
  } else {
    $fullPath = Join-Path $Root $FilePath
  }

  $phase = $null
  $step = $null
  $done = $null
  $latest_step = $null
  $step_count = 0
  $phase_summary_exists = $false

  $phaseStatePath = Join-Path $Root "workspace\artifacts\phase_state.json"
  if (Test-Path $phaseStatePath) {
    $state = Get-Content $phaseStatePath -Encoding UTF8 | ConvertFrom-Json
    $phase = $state.current_phase
    $step = $state.current_step
    $done = $state.last_done
  }

  $stepsDir = Join-Path $Root "logs\steps"
  $stepFiles = Get-ChildItem -Path $stepsDir -Filter "step_*.json" -ErrorAction SilentlyContinue | Sort-Object Name -Descending
  if ($stepFiles.Count -gt 0) {
    $latest_step = $stepFiles[0].Name
    $step_count = $stepFiles.Count
  }

  $phaseSummaryPath = Join-Path $Root "logs\phase_summary.json"
  if (Test-Path $phaseSummaryPath) {
    $phase_summary_exists = $true
  }

  # Save JSON
  $summary = @{
    phase = $phase
    step = $step
    done = $done
    latest_step = $latest_step
    step_count = $step_count
    phase_summary_exists = $phase_summary_exists
  }
  $summary | ConvertTo-Json -Depth 10 | Set-Content -Path $fullPath -Encoding UTF8

  # Save TXT (same base name with .txt extension)
  $txtPath = [System.IO.Path]::ChangeExtension($fullPath, ".txt")
  $phaseSummaryText = if ($phase_summary_exists) { "exists" } else { "none" }
  $txtContent = "phase=$phase step=$step done=$done latest_step=$latest_step step_count=$step_count phase_summary=$phaseSummaryText"
  $txtContent | Set-Content -Path $txtPath -Encoding UTF8

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
  } else {
    # CL: Check for deny/fatal_error phase
    $state = Get-Content $phaseState -Encoding UTF8 | ConvertFrom-Json
    if ($state.current_phase -eq "deny") {
      Write-Host "FAIL phase is deny: $($state.last_done_reason)"
      $testPassed = $false
    }
    if ($state.current_phase -eq "fatal_error") {
      Write-Host "FAIL phase is fatal_error: $($state.last_done_reason)"
      $testPassed = $false
    }
  }

  # Check step files
  $stepsDir = Join-Path $Root "logs\steps"
  $stepFiles = Get-ChildItem -Path $stepsDir -Filter "step_*.json" -ErrorAction SilentlyContinue
  if ($stepFiles.Count -eq 0) {
    Write-Host "FAIL no step files found"
    $testPassed = $false
  }

  # DK: Check for stopped=true in any step
  if ($stepFiles.Count -gt 0) {
    foreach ($sf in $stepFiles) {
      $stepData = Get-Content $sf.FullName -Encoding UTF8 | ConvertFrom-Json
      if ($stepData.stopped -eq $true) {
        Write-Host "FAIL step $($sf.Name) stopped=true phase=$($stepData.phase)"
        $testPassed = $false
      }
    }
  }

  # IH: S-5 experimental warning (does not affect exit code)
  if ($stepFiles.Count -gt 0) {
    $latestStepForExp = Get-Content $stepFiles[0].FullName -Encoding UTF8 | ConvertFrom-Json
    if ($latestStepForExp.is_experimental -eq $true) {
      $stateForExp = Get-Content $phaseState -Encoding UTF8 | ConvertFrom-Json
      if ($stateForExp.current_phase -eq "S-5") {
        Write-Host "WARNING: S-5 experimental mode - results may be unstable"
      }
    }
  }

  if ($testPassed) {
    Write-Host "test passed"
  } else {
    Write-Host "test failed"
  }

  # Save summary if specified (after test result)
  if ($SummaryFile) {
    Save-Summary -FilePath $SummaryFile
  }

  if ($testPassed) {
    exit 0
  } else {
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
$exitWithError = $false
if (Test-Path $phaseState) {
  $state = Get-Content $phaseState -Encoding UTF8 | ConvertFrom-Json
  # IE: S-5 experimental display
  $phaseDisplay = $state.current_phase
  if ($state.current_phase -eq "S-5") {
    $phaseDisplay = "$($state.current_phase) (experimental)"
  }
  Write-Host "phase_state phase=$phaseDisplay step=$($state.current_step) done=$($state.last_done)"
  # DJ: Priority order: fatal_error > deny > stopped
  # CH: fatal_error phase: show fatal_error reason and exit 1
  if ($state.current_phase -eq "fatal_error") {
    Write-Host "fatal_error $($state.last_done_reason)"
    $exitWithError = $true
  }
  # CG: deny phase: show deny reason and exit 1
  elseif ($state.current_phase -eq "deny") {
    Write-Host "deny $($state.last_done_reason)"
    $exitWithError = $true
  }
} else {
  Write-Host "phase_state none"
}

# DI: Check latest step for stopped=true
$stepsDir = Join-Path $Root "logs\steps"
$stepFilesForStopped = Get-ChildItem -Path $stepsDir -Filter "step_*.json" -ErrorAction SilentlyContinue | Sort-Object Name -Descending
if ($stepFilesForStopped.Count -gt 0) {
  $latestStepData = Get-Content $stepFilesForStopped[0].FullName -Encoding UTF8 | ConvertFrom-Json
  if ($latestStepData.stopped -eq $true) {
    Write-Host "stopped phase=$($latestStepData.phase) step=$($latestStepData.step_num)"
  }
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
  $summaryData = Get-Content $phaseSummary -Encoding UTF8 | ConvertFrom-Json
  # DQ: Show stop_on_deny setting
  Write-Host "phase_summary exists stop_on_deny=$($summaryData.stop_on_deny)"
  # DT: Show end_reason if exists
  if ($summaryData.end_reason) {
    Write-Host "end_reason $($summaryData.end_reason)"
  }
} else {
  Write-Host "phase_summary none"
}

# Save summary if specified
if ($SummaryFile) {
  Save-Summary -FilePath $SummaryFile
}

Write-Host "TOS cc_run end"
if ($exitWithError) {
  exit 1
}
exit 0
