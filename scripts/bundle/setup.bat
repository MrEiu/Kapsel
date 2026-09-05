@echo off
title Kapsel 官方完整版一键安装程序
echo ============================================================
echo   正在启动 Kapsel 官方完整版一键快速部署...
echo ============================================================
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
echo.
echo 请按任意键退出...
pause >nul
