#!/bin/bash

# 播客对话生成器 - 启动脚本
# 作者: 自动生成
# 描述: 启动FastAPI应用服务

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$PROJECT_ROOT/app"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$PROJECT_ROOT/app.pid"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 函数：输出彩色信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 函数：检查应用是否已在运行
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# 函数：启动应用
start_application() {
    print_info "正在启动播客对话生成器..."
    
    # 检查是否已安装Python
    if ! command -v python3 &> /dev/null; then
        print_error "未找到Python3，请先安装Python3"
        exit 1
    fi
    
    # 检查是否已安装依赖
    if [ ! -f "$PROJECT_ROOT/requirements.txt" ]; then
        print_error "未找到requirements.txt文件"
        exit 1
    fi
    
    # 检查并安装依赖
    print_info "检查Python依赖..."
    pip3 install -r "$PROJECT_ROOT/requirements.txt"
    
    # 切换到应用目录
    cd "$APP_DIR"
    
    # 启动FastAPI应用（使用uvicorn）
    print_info "启动FastAPI服务..."
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/app.log" 2>&1 &
    
    # 保存进程ID
    echo $! > "$PID_FILE"
    
    # 等待应用启动
    sleep 3
    
    # 检查是否启动成功
    if check_running; then
        print_info "✅ 应用启动成功！"
        print_info "📊 应用日志: $LOG_DIR/app.log"
        print_info "🌐 访问地址: http://localhost:8000"
        print_info "📚 API文档: http://localhost:8000/docs"
        print_info "🆔 进程ID: $(cat $PID_FILE)"
    else
        print_error "❌ 应用启动失败，请检查日志: $LOG_DIR/app.log"
        exit 1
    fi
}

# 函数：停止应用
stop_application() {
    print_info "正在停止播客对话生成器..."
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            sleep 2
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID
            fi
            print_info "✅ 应用已停止 (PID: $PID)"
        else
            print_warning "应用未在运行"
        fi
        rm -f "$PID_FILE"
    else
        print_warning "未找到PID文件，应用可能未启动"
    fi
}

# 函数：查看应用状态
status_application() {
    if check_running; then
        PID=$(cat "$PID_FILE")
        print_info "✅ 应用正在运行 (PID: $PID)"
        print_info "🌐 访问地址: http://localhost:8000"
    else
        print_info "❌ 应用未运行"
    fi
}

# 函数：查看应用日志
tail_logs() {
    if [ -f "$LOG_DIR/app.log" ]; then
        tail -f "$LOG_DIR/app.log"
    else
        print_error "日志文件不存在"
    fi
}

# 主程序
case "$1" in
    start)
        if check_running; then
            print_warning "应用已在运行 (PID: $(cat $PID_FILE))"
        else
            start_application
        fi
        ;;
    stop)
        stop_application
        ;;
    restart)
        stop_application
        sleep 2
        start_application
        ;;
    status)
        status_application
        ;;
    logs)
        tail_logs
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "命令说明:"
        echo "  start   启动应用服务"
        echo "  stop    停止应用服务"
        echo "  restart 重启应用服务"
        echo "  status  查看应用状态"
        echo "  logs    实时查看应用日志"
        echo ""
        exit 1
        ;;
esac