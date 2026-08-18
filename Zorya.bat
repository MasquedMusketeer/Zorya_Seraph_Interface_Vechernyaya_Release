@echo off
title Zorya Vigil Protocol   Designation: M.I.D.A.S.

REM Check for admin privileges, relaunch elevated if not
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)


cd /d "%~dp0"


REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Running dependency installer...
    call install_dependencies.bat
    echo.
    echo Please restart this script after installation.
    pause
    exit /b
)

REM Run the program
python Zorya.py
