@echo off
chcp 65001 >nul
title 播客对话生成器 - 停止服务

echo ========================================
echo   播客对话生成器 - 停止脚本
echo ========================================
echo.

echo [信息] 正在查找并停止FastAPI进程...

:: 查找uvicorn进程
for /f "tokens=2" %%i in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    set /a PID=%%i
    echo 找到进程PID: !PID!
    taskkill /PID !PID! /F
    if errorlevel 1 (
        echo [错误] 无法停止进程 !PID!
    ) else (
        echo [成功] 已停止进程 !PID!
    )
)

:: 额外的进程查找
tasklist /fi "imagename eq python.exe" /fo table | findstr /i "uvicorn" >nul
if not errorlevel 1 (
    echo [信息] 查找uvicorn相关进程...
    taskkill /fi "imagename eq python.exe" /fi "windowtitle eq uvicorn*" /f
)

echo [信息] 服务停止完成
timeout /t 3 >nul