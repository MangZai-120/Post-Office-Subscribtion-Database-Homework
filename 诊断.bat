@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   环境诊断 - 检查你的电脑能不能跑这个系统
echo ============================================
echo.
REM 自动找 Python
set "PYEXE="
where py >nul 2>&1 && set "PYEXE=py"
if not defined PYEXE where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE (
    echo [错误] 找不到 Python！请先安装 Python 3.10+
    echo 下载: https://www.python.org/downloads/  (安装时勾选 Add to PATH)
    echo.
    pause
    exit /b 1
)
%PYEXE% "诊断.py"
pause
