# EB/EI/ES/GR: checkpoint.ps1
param(
  [string]$Root = "C:\Users\takag\00_dev\tos",
  [string]$Name
)

function Show-Usage {
  Write-Host "usage checkpoint.ps1 -Name <text>"
}

# EI: Check required parameter
if (-not $Name) {
  Show-Usage
  exit 1
}

Set-Location $Root

# ES: git add . (even if dirty)
git add . 2>$null

# EB: git commit
$commitMsg = "CHECKPOINT $Name"
$output = git commit -m $commitMsg --allow-empty 2>&1
$commitExitCode = $LASTEXITCODE

if ($commitExitCode -ne 0) {
  Write-Host "git commit failed"
  exit 1
}

# GR: Output only commit hash (no extra lines)
$hash = git rev-parse HEAD
Write-Output $hash
exit 0
