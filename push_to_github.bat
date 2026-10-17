@echo off
setlocal enabledelayedexpansion
title ScamShield AI - GitHub Push Assistant
color 0b

echo ==========================================================
echo       ScamShield AI - Automated GitHub Push Assistant
echo ==========================================================
echo.

:: Add MinGit and GitHub CLI to session PATH
set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd;%LOCALAPPDATA%\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin;%PATH%"

echo [*] Checking Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Git not found.
    pause
    exit /b 1
)
echo [OK] Git is available.

echo.
echo ==========================================================
echo  Choose how you want to push to GitHub:
echo ==========================================================
echo  [1] Automatic: Sign in with GitHub CLI and create repository automatically (Recommended)
echo  [2] Manual: I already created a repository and have the URL (https://github.com/...)
echo ==========================================================
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo.
    echo [*] Checking GitHub authentication status...
    gh auth status >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] You are not signed into GitHub yet.
        echo [!] Opening GitHub Web Login in your browser...
        echo.
        gh auth login --web --git-protocol https
    )
    
    echo.
    echo [*] Creating GitHub repository 'scamshield-ai' and pushing code...
    gh repo create scamshield-ai --public --source="%~dp0." --remote=origin --push
    
    if %errorlevel% equ 0 (
        echo.
        echo ==========================================================
        echo [SUCCESS] ScamShield AI has been pushed to your GitHub!
        echo ==========================================================
    ) else (
        echo.
        echo [!] Note: If the repository already exists, pushing directly:
        git push -u origin main
    )
) else (
    echo.
    set /p repo_url="Enter your GitHub repository URL: "
    if not "!repo_url!"=="" (
        git remote remove origin >nul 2>&1
        git remote add origin !repo_url!
        git branch -M main
        echo [*] Pushing to !repo_url!...
        git push -u origin main
    ) else (
        echo [!] No URL provided.
    )
)

echo.
echo Done. Press any key to exit.
pause >nul
