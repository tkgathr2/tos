# EB/EI/ES: checkpoint.ps1
param(
  [string]$Root = "C:\Users\takag\00_dev\tos",
  [string]$Name
)

$ErrorActionPreference = "Stop"

function Show-Usage {
  Write-Host "usage checkpoint.ps1 -Name <text>"
}

# EI: Check required parameter
if (-not $Name) {
  Show-Usage
  exit 1
}

Write-Host "checkpoint start"
Write-Host "Root $Root"
Write-Host "Name $Name"

Set-Location $Root

# ES: git status
Write-Host "git status"
git status

# ES: git add . (even if dirty)
Write-Host "git add ."
git add .

# EB: git commit
$commitMsg = "CHECKPOINT $Name"
Write-Host "git commit -m `"$commitMsg`""
git commit -m $commitMsg --allow-empty
if ($LASTEXITCODE -ne 0) {
  Write-Host "git commit failed"
  exit 1
}

# EB: Output commit hash
$hash = git rev-parse HEAD
Write-Host $hash

Write-Host "checkpoint done"
exit 0
