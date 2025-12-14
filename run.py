#!/usr/bin/env python3
"""
播客对话生成器 - 统一启动脚本
支持跨平台运行：python run.py [start|stop|restart|status]
"""

import os
import sys
import time
import signal
import subprocess
import platform
from pathlib import Path

class FastAPIManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_dir = self.project_root / "app"
        self.log_dir = self.project_root / "logs"
        self.pid_file = self.project_root / "app.pid"
        
        # 创建日志目录
        self.log_dir.mkdir(exist_ok=True)
        
        self.log_file = self.log_dir / "app.log"
        
    def print_info(self, message):
        print(f"📊 [INFO] {message}")
        
    def print_success(self, message):
        print(f"✅ [SUCCESS] {message}")
        
    def print_error(self, message):
        print(f"❌ [ERROR] {message}")
        
    def print_warning(self, message):
        print(f"⚠️ [WARNING] {message}")
    
    def is_running(self):
        """检查应用是否在运行"""
        if self.pid_file.exists():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            try:
                # 检查进程是否存在
                if platform.system() == "Windows":
                    result = subprocess.run(f"tasklist /fi \"PID eq {pid}\"", 
                                          capture_output=True, text=True, shell=True)
                    return str(pid) in result.stdout
                else:
                    os.kill(pid, 0)
                    return True
            except (OSError, subprocess.SubprocessError):
                self.pid_file.unlink(missing_ok=True)
                return False
        return False
    
    def start(self):
        """启动应用"""
        if self.is_running():
            self.print_warning("应用已在运行中")
            return True
            
        self.print_info("正在启动播客对话生成器...")
        
        # 检查Python依赖
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            self.print_info("安装Python依赖...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        
        # 启动应用
        os.chdir(self.app_dir)
        
        # 使用uvicorn启动FastAPI应用
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        # 根据平台选择启动方式
        if platform.system() == "Windows":
            import subprocess as sp
            process = sp.Popen(
                cmd,
                stdout=open(self.log_file, 'w'),
                stderr=sp.STDOUT,
                creationflags=sp.CREATE_NEW_PROCESS_GROUP
            )
        else:
            import subprocess as sp
            process = sp.Popen(
                cmd,
                stdout=open(self.log_file, 'w'),
                stderr=sp.STDOUT,
                preexec_fn=os.setpgrp
            )
        
        # 保存PID
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        
        # 等待启动
        time.sleep(5)
        
        if self.is_running():
            self.print_success("应用启动成功！")
            self.print_info(f"访问地址: http://localhost:8000")
            self.print_info(f"API文档: http://localhost:8000/docs")
            self.print_info(f"进程PID: {process.pid}")
            self.print_info(f"日志文件: {self.log_file}")
            return True
        else:
            self.print_error("应用启动失败，请检查日志文件")
            return False
    
    def stop(self):
        """停止应用"""
        if not self.is_running():
            self.print_warning("应用未在运行")
            return True
            
        self.print_info("正在停止应用...")
        
        if self.pid_file.exists():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(f"taskkill /PID {pid} /F", shell=True)
                else:
                    os.killpg(pid, signal.SIGTERM)
                    time.sleep(2)
                    if self.is_running():
                        os.killpg(pid, signal.SIGKILL)
                
                self.pid_file.unlink(missing_ok=True)
                self.print_success("应用已停止")
                return True
                
            except ProcessLookupError:
                self.print_warning("进程不存在")
                self.pid_file.unlink(missing_ok=True)
                return True
            except Exception as e:
                self.print_error(f"停止应用时出错: {e}")
                return False
    
    def restart(self):
        """重启应用"""
        self.stop()
        time.sleep(2)
        return self.start()
    
    def status(self):
        """查看应用状态"""
        if self.is_running():
            with open(self.pid_file, 'r') as f:
                pid = f.read().strip()
            self.print_success(f"应用正在运行 (PID: {pid})")
            self.print_info(f"访问地址: http://localhost:8000")
        else:
            self.print_info("应用未运行")
    
    def show_usage(self):
        """显示使用说明"""
        print("播客对话生成器 - 应用管理脚本")
        print("=" * 50)
        print("使用方法: python run.py <command>")
        print()
        print("命令列表:")
        print("  start    启动应用服务")
        print("  stop     停止应用服务")
        print("  restart  重启应用服务")
        print("  status   查看应用状态")
        print("  logs     查看应用日志")
        print()
        print("示例:")
        print("  python run.py start    # 启动应用")
        print("  python run.py status   # 查看状态")

def main():
    if len(sys.argv) != 2:
        FastAPIManager().show_usage()
        sys.exit(1)
    
    manager = FastAPIManager()
    command = sys.argv[1].lower()
    
    if command == "start":
        success = manager.start()
        sys.exit(0 if success else 1)
    elif command == "stop":
        success = manager.stop()
        sys.exit(0 if success else 1)
    elif command == "restart":
        success = manager.restart()
        sys.exit(0 if success else 1)
    elif command == "status":
        manager.status()
    elif command == "logs":
        if manager.log_file.exists():
            subprocess.run(["tail", "-f", str(manager.log_file)])
        else:
            print("日志文件不存在")
    else:
        print(f"未知命令: {command}")
        manager.show_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()