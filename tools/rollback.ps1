# EA/EH: rollback.ps1
param(
  [string]$Root = "C:\Users\takag\00_dev\tos",
  [string]$TargetCommit
)

$ErrorActionPreference = "Stop"

function Show-Usage {
  Write-Host "usage rollback.ps1 -TargetCommit <hash>"
}

# EH: Check required parameter
if (-not $TargetCommit) {
  Show-Usage
  exit 1
}

Write-Host "rollback start"
Write-Host "Root $Root"
Write-Host "TargetCommit $TargetCommit"

Set-Location $Root

# EA: git fetch
Write-Host "git fetch"
git fetch

# EA: git reset --hard
Write-Host "git reset --hard $TargetCommit"
git reset --hard $TargetCommit
if ($LASTEXITCODE -ne 0) {
  Write-Host "git reset failed"
  exit 1
}

# EA: git clean -fd
Write-Host "git clean -fd"
git clean -fd

Write-Host "rollback done"
exit 0
