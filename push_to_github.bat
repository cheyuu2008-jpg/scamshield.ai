@echo off
title ScamShield AI - Push to GitHub
color 0b
echo ==========================================================
echo    ScamShield AI - GitHub Automated Push Assistant
echo ==========================================================
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0push_to_github.ps1"
echo.
pause
