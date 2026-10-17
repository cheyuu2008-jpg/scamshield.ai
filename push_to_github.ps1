<#
.SYNOPSIS
    Automated Git initialization, commit, and push script for ScamShield AI.
.DESCRIPTION
    Initializes git repository, adds files, commits, and pushes to your GitHub repo.
#>

param (
    [string]$RepoUrl = ""
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🛡️  ScamShield AI - GitHub Automated Push Utility" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Refresh environment path to detect newly installed Git
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Check if git is available
$gitPath = ""
if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitPath = "git"
} elseif (Test-Path "C:\Program Files\Git\cmd\git.exe") {
    $gitPath = "C:\Program Files\Git\cmd\git.exe"
    $env:Path += ";C:\Program Files\Git\cmd"
} elseif (Test-Path "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe") {
    $gitPath = "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe"
    $env:Path += ";$env:LOCALAPPDATA\Programs\Git\cmd"
}

if (-not $gitPath) {
    Write-Host "❌ Error: Git is not installed or not in PATH." -ForegroundColor Red
    Write-Host "👉 Please install Git from https://git-scm.com/download/win and rerun this script." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git detected: $(& $gitPath --version)" -ForegroundColor Green

# 1. Initialize Git Repo
if (-not (Test-Path ".git")) {
    Write-Host "📁 Initializing new Git repository..." -ForegroundColor Yellow
    & $gitPath init -b main
} else {
    Write-Host "📁 Existing Git repository detected." -ForegroundColor Cyan
}

# 2. Check Git User Configuration
$currentName = & $gitPath config user.name
$currentEmail = & $gitPath config user.email

if (-not $currentName) {
    Write-Host "⚙️ Setting local Git username..." -ForegroundColor Yellow
    & $gitPath config user.name "ScamShield Developer"
}
if (-not $currentEmail) {
    Write-Host "⚙️ Setting local Git email..." -ForegroundColor Yellow
    & $gitPath config user.email "dev@scamshield.ai"
}

# 3. Add files and Commit
Write-Host "📦 Staging project files..." -ForegroundColor Yellow
& $gitPath add .

$status = & $gitPath status --porcelain
if ($status) {
    Write-Host "💾 Creating commit..." -ForegroundColor Yellow
    & $gitPath commit -m "Initial release: ScamShield AI Hackathon Prototype (Multi-Vector Fraud Interceptor)"
    Write-Host "✅ Commit created successfully." -ForegroundColor Green
} else {
    Write-Host "ℹ️ Working directory clean, no new changes to commit." -ForegroundColor Cyan
}

# 4. Handle Remote Repository URL
if (-not $RepoUrl) {
    $existingRemote = & $gitPath remote get-url origin 2>$null
    if ($existingRemote) {
        Write-Host "🔗 Current origin remote: $existingRemote" -ForegroundColor Cyan
        $RepoUrl = $existingRemote
    } else {
        Write-Host ""
        Write-Host "----------------------------------------------------------" -ForegroundColor Yellow
        Write-Host "🌐 Please enter your GitHub repository URL:" -ForegroundColor White
        Write-Host "   Example: https://github.com/your-username/scamshield-ai.git" -ForegroundColor Gray
        Write-Host "----------------------------------------------------------" -ForegroundColor Yellow
        $RepoUrl = Read-Host "GitHub Repo URL"
    }
}

if (-not $RepoUrl) {
    Write-Host "⚠️ No repository URL provided. Local Git commit is ready!" -ForegroundColor Yellow
    Write-Host "👉 When your GitHub repo is ready, run:" -ForegroundColor White
    Write-Host "   git remote add origin <YOUR_GITHUB_REPO_URL>" -ForegroundColor Gray
    Write-Host "   git push -u origin main" -ForegroundColor Gray
    exit 0
}

# 5. Add or update remote origin
$hasOrigin = & $gitPath remote
if ($hasOrigin -contains "origin") {
    & $gitPath remote set-url origin $RepoUrl
} else {
    & $gitPath remote add origin $RepoUrl
}

# 6. Push to GitHub
Write-Host "🚀 Pushing code to GitHub ($RepoUrl)..." -ForegroundColor Yellow
& $gitPath branch -M main
& $gitPath push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SUCCESS! Your ScamShield AI project has been pushed to GitHub!" -ForegroundColor Green
    Write-Host "🔗 View your repository at: $RepoUrl" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "⚠️ Push encountered an issue (authentication or repository not created yet)." -ForegroundColor Yellow
    Write-Host "👉 Tip: Ensure your GitHub repo is created on github.com and you have sign-in permissions." -ForegroundColor Gray
}
