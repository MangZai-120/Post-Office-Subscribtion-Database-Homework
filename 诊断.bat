@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Environment Diagnostic
echo ============================================
echo.
set "PYEXE="
where py >nul 2>&1 && set "PYEXE=py"
if not defined PYEXE where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
%PYEXE% diagnose.py
pause