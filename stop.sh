#!/bin/bash

# 播客对话生成器 - 停止脚本
# 描述: 专门用于停止FastAPI应用服务

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$PROJECT_ROOT/app.pid"

# 颜色设置
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}[INFO]${NC} 正在停止播客对话生成器..."

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    if ps -p $PID > /dev/null 2>&1; then
        echo -e "${GREEN}[INFO]${NC} 找到运行中的进程 (PID: $PID)，正在停止..."
        
        # 尝试优雅停止
        kill $PID
        sleep 5
        
        # 检查进程是否仍在运行
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${RED}[WARNING]${NC} 进程仍在运行，强制停止..."
            kill -9 $PID
            sleep 2
        fi
        
        if ps -p $PID > /dev/null 2>&1; then
            echo -e "${RED}[ERROR]${NC} 无法停止进程 $PID"
            exit 1
        else
            echo -e "${GREEN}[SUCCESS]${NC} ✅ 应用已成功停止"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${RED}[WARNING]${NC} 进程 $PID 不存在"
        rm -f "$PID_FILE"
    fi
else
    echo -e "${RED}[ERROR]${NC} 未找到PID文件，应用可能未启动"
    echo "正在查找可能的FastAPI进程..."
    
    # 查找可能的uvicorn进程
    PIDS=$(ps aux | grep "uvicorn" | grep -v grep | awk '{print $2}')
    
    if [ -z "$PIDS" ]; then
        echo -e "${GREEN}[INFO]${NC} 未找到运行的FastAPI进程"
    else
        echo -e "${YELLOW}[INFO]${NC} 找到以下可能的FastAPI进程:"
        ps aux | grep "uvicorn" | grep -v grep
        echo ""
        read -p "是否停止这些进程？(y/n): " choice
        case "$choice" in
            y|Y)
                for PID in $PIDS; do
                    echo "停止进程 $PID"
                    kill $PID
                done
                echo -e "${GREEN}[SUCCESS]${NC} 所有相关进程已停止"
                ;;
            *)
                echo "操作已取消"
                ;;
        esac
    fi
fi