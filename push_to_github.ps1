<#
.SYNOPSIS
    Automated Git push script for ScamShield AI to https://github.com/cheyuu2008-jpg/scamshield.ai.git
#>

param (
    [string]$RepoUrl = "https://github.com/cheyuu2008-jpg/scamshield.ai.git"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🛡️  ScamShield AI - GitHub Push Assistant" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Locate Git
$gitPath = ""
$candidates = @(
    "C:\Users\kumary shreya\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe",
    "C:\Program Files\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
)

foreach ($c in $candidates) {
    if (Test-Path $c) {
        $gitPath = $c
        break
    }
}

if (-not $gitPath) {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $gitPath = "git"
    } else {
        Write-Host "Error: Git binary could not be found." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Using Git: $gitPath" -ForegroundColor Green
& $gitPath --version

# Set repo remote
Write-Host "Target Repository: $RepoUrl" -ForegroundColor Cyan
& $gitPath remote set-url origin $RepoUrl 2>$null
if ($LASTEXITCODE -ne 0) {
    & $gitPath remote add origin $RepoUrl
}

# Ensure everything is staged and committed
Write-Host "Ensuring all files are committed..." -ForegroundColor Yellow
& $gitPath add .
$status = & $gitPath status --porcelain
if ($status) {
    & $gitPath commit -m "Update: ScamShield AI Hackathon Prototype"
} else {
    Write-Host "Working tree is clean." -ForegroundColor Green
}

# Check branch
& $gitPath branch -M main

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host "Pushing branch 'main' to GitHub..." -ForegroundColor Yellow
Write-Host "When prompted for credentials:" -ForegroundColor White
Write-Host " - Username: cheyuu2008-jpg" -ForegroundColor Cyan
Write-Host " - Password: Use your GitHub Personal Access Token (PAT)" -ForegroundColor Cyan
Write-Host "   (Generate one at: https://github.com/settings/tokens)" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host ""

& $gitPath push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS! Code has been pushed to: $RepoUrl" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Push notice: If authentication failed, use a Personal Access Token." -ForegroundColor Yellow
    Write-Host 'Command: git push https://<TOKEN>@github.com/cheyuu2008-jpg/scamshield.ai.git main' -ForegroundColor Cyan
}
