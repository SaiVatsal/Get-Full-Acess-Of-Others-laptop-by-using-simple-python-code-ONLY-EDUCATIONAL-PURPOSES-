@echo off
title Disable Antivirus (Windows Defender)

:: ------------------------------------------------------------------
:: WARNING: Disabling antivirus exposes your system to threats.
:: Only do this temporarily for a specific task and re-enable it afterwards.
:: ------------------------------------------------------------------

:: Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges.
    echo Please right-click the file and select "Run as administrator".
    pause
    exit /b 1
)

echo Disabling Windows Defender real-time monitoring...
powershell -command "Set-MpPreference -DisableRealtimeMonitoring $true"

if %errorLevel% equ 0 (
    echo [OK] Real-time protection is now disabled.
) else (
    echo [FAIL] Could not disable protection. It might be managed by Group Policy or another security product.
)

echo.
echo To re-enable, run the following command as Administrator:
echo   powershell -command "Set-MpPreference -DisableRealtimeMonitoring $false"
pause