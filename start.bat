@echo off
chcp 65001 >nul
title 播客对话生成器 - 启动服务

echo ========================================
echo   播客对话生成器 - 启动脚本
echo ========================================
echo.

set PROJECT_ROOT=%~dp0
set APP_DIR=%PROJECT_ROOT%app
set LOG_DIR=%PROJECT_ROOT%logs

:: 创建日志目录
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

:: 检查requirements.txt
if not exist "%PROJECT_ROOT%requirements.txt" (
    echo [错误] 未找到requirements.txt文件
    pause
    exit /b 1
)

:: 安装依赖
echo [信息] 检查并安装Python依赖...
pip install -r "%PROJECT_ROOT%requirements.txt"

:: 切换到应用目录
cd /d "%APP_DIR%"

:: 检查是否已在运行
netstat -an | findstr ":8000" >nul
if not errorlevel 1 (
    echo [警告] 端口8000已被占用，应用可能已在运行
    echo 访问地址: http://localhost:8000
    pause
    exit /b 0
)

:: 启动应用
echo [信息] 启动FastAPI服务...
echo 启动时间: %date% %time% > "%LOG_DIR%\app.log"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 >> "%LOG_DIR%\app.log" 2>&1

if errorlevel 1 (
    echo [错误] 应用启动失败，请检查日志: %LOG_DIR%\app.log
    pause
    exit /b 1
)

echo [成功] 应用启动完成！
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
pause