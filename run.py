#!/usr/bin/env python3
"""
播客对话生成器 - 统一启动脚本
支持跨平台运行：python run.py [start|stop|restart|status]
"""

import os
import socket
import sys
import time
import signal
import subprocess
import platform
from pathlib import Path
import argparse
import re
import importlib.metadata as importlib_metadata

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
        print(f"ℹ️  {message}", flush=True)
        
    def print_success(self, message):
        print(f"✓ {message}", flush=True)
        
    def print_error(self, message):
        print(f"✗ {message}", flush=True)
        
    def print_warning(self, message):
        print(f"⚠ {message}", flush=True)
    
    def is_running(self):
        """检查应用是否在运行"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    content = f.read().strip()
                    pid = int(content)
            except (ValueError, FileNotFoundError):
                # PID 文件内容无效或文件不存在，尝试删除并返回 False
                try:
                    self.pid_file.unlink(missing_ok=True)
                except Exception:
                    pass
                return False

            try:
                # 检查进程是否存在
                if platform.system() == "Windows":
                    result = subprocess.run(f"tasklist /fi \"PID eq {pid}\"", 
                                            capture_output=True, text=True, shell=True)
                    if str(pid) in result.stdout:
                        return True
                    # 进程不存在，删除过期的 pid 文件
                    try:
                        self.pid_file.unlink(missing_ok=True)
                    except Exception:
                        pass
                    return False
                else:
                    os.kill(pid, 0)
                    return True
            except (OSError, subprocess.SubprocessError):
                try:
                    self.pid_file.unlink(missing_ok=True)
                except Exception:
                    pass
                return False
        return False

    def _is_port_in_use(self, host: str = "127.0.0.1", port: int = 4190) -> bool:
        """检查本地端口是否有服务在监听（通过尝试连接）。"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((host, port))
                return result == 0
        except Exception:
            return False

    def _print_progress(self, current: int, total: int, message: str):
        try:
            pct = int((current / total) * 100) if total else 100
            print(f"[{current}/{total}] {message} ({pct}%)", flush=True)
        except Exception:
            print(f"{message}", flush=True)

    def _install_missing_requirements(self, requirements_file: Path):
        """读取 requirements.txt，检查本地已安装包，安装缺失项。"""
        if not requirements_file.exists():
            return

        try:
            installed = { (d.metadata.get('Name') or '').lower() for d in importlib_metadata.distributions() }
        except Exception:
            installed = set()

        to_install = []
        for raw in requirements_file.read_text(encoding='utf-8').splitlines():
            line = raw.split('#', 1)[0].strip()
            if not line:
                continue
            # 保持原始可安装项（可能包含版本约束或 URL）
            if line.startswith('-e') or line.startswith('git+') or line.startswith('http'):
                to_install.append(line)
                continue
            # 解析包名（取第一个版本比较符之前的部分）
            name = re.split(r"[<>=!~]", line, 1)[0].strip()
            if not name:
                continue
            if name.lower() not in installed:
                to_install.append(line)

        if not to_install:
            return

        total = len(to_install)
        self.print_info("正在安装缺失的依赖...")

        for idx, pkg in enumerate(to_install, start=1):
            self._print_progress(idx, total, f"安装 {pkg}")
            cmd = [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-warn-script-location', '--progress-bar', 'on', pkg]
            try:
                res = subprocess.run(cmd, check=False)
                if res.returncode == 0:
                    self._print_progress(idx, total, f"已安装 {pkg}")
                else:
                    self.print_warning(f"安装失败: {pkg}")
            except Exception as e:
                self.print_error(f"安装依赖时出错: {e}")
        self.print_info("依赖安装完成")

    def _get_pid_by_port(self, port: int = 4190):
        """在 Windows 上尝试通过 netstat 查找占用指定端口的 PID；其他平台返回 None。"""
        try:
            if platform.system() == 'Windows':
                output = subprocess.check_output('netstat -ano', shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    parts = line.split()
                    if len(parts) >= 5 and parts[0] == 'TCP':
                        local = parts[1]
                        pid = parts[-1]
                        if local.endswith(f':{port}'):
                            try:
                                return int(pid)
                            except Exception:
                                continue
            else:
                # 尝试使用 lsof（如果可用）
                try:
                    output = subprocess.check_output(['lsof', '-i', f':{port}', '-Pn'], text=True, stderr=subprocess.DEVNULL)
                    for line in output.splitlines()[1:]:
                        cols = line.split()
                        if len(cols) >= 2:
                            try:
                                return int(cols[1])
                            except Exception:
                                continue
                except Exception:
                    return None
        except Exception:
            return None
        return None
    
    def _check_api_config(self):
        """检查API配置是否有效"""

        try:
            # 检查千问API配置（用于对话生成和TTS）
            sys.path.insert(0, str(self.app_dir))
            from qwen import _CLIENT, _CLIENT_PROVIDER
            
            # 检查环境变量中的配置
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            # 检查千问API配置
            api_configured = False
            dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
            
            # 如果API密钥缺失，允许用户在控制台输入
            if not dashscope_api_key:
                self.print_info("未检测到千问API密钥配置")
                self.print_info("正在打开千问API配置指导网页...")
                
                # 自动打开配置指导网页
                try:
                    import webbrowser
                    # 打开千问API配置指导网页
                    qwen_url = "https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen"
                    self.print_info(f"正在打开千问API配置指导网页: {qwen_url}")
                    webbrowser.open(qwen_url)
                except Exception as e:
                    self.print_warning(f"无法自动打开网页: {e}")
                
                self.print_info("")
                self.print_info("您可以直接在控制台输入API密钥进行配置")
                self.print_info("请输入千问API密钥（输入时不会显示）：")
                
                # 读取用户输入的API密钥，不显示输入内容
                import getpass
                try:
                    dashscope_api_key = getpass.getpass()
                    if dashscope_api_key:
                        # 将API密钥写入.env文件
                        # 确保使用项目根目录的绝对路径
                        import os
                        env_file = os.path.join(str(self.project_root), ".env")
                        self.print_info(f"项目根目录: {self.project_root}")
                        self.print_info(f"正在写入API密钥到文件: {env_file}")
                        
                        try:
                            if os.path.exists(env_file):
                                # 读取现有内容
                                with open(env_file, "r", encoding="utf-8") as f:
                                    lines = f.readlines()
                                
                                # 更新或添加DASHSCOPE_API_KEY
                                updated_lines = []
                                found = False
                                for line in lines:
                                    if line.startswith("DASHSCOPE_API_KEY="):
                                        updated_lines.append(f"DASHSCOPE_API_KEY={dashscope_api_key}\n")
                                        found = True
                                    else:
                                        updated_lines.append(line)
                                
                                if not found:
                                    updated_lines.append(f"DASHSCOPE_API_KEY={dashscope_api_key}\n")
                                
                                # 写回文件
                                with open(env_file, "w", encoding="utf-8") as f:
                                    f.writelines(updated_lines)
                                self.print_info("已更新现有.env文件")
                            else:
                                # 创建新的.env文件，使用合理的格式
                                with open(env_file, "w", encoding="utf-8") as f:
                                    f.write("# API配置\n")
                                    f.write("# 千问API密钥（用于对话生成和TTS）\n")
                                    f.write(f"DASHSCOPE_API_KEY={dashscope_api_key}\n")
                                    f.write("\n")
                                    f.write("# 其他配置（可选）\n")
                                    f.write("# MODEL=deepseek-v3.2\n")
                                self.print_info("已创建新的.env文件")
                            
                            # 验证文件是否创建成功
                            if os.path.exists(env_file):
                                file_size = os.path.getsize(env_file)
                                self.print_info(f".env文件创建成功，大小: {file_size} 字节")
                                # 读取并显示文件内容（隐藏API密钥）
                                with open(env_file, "r", encoding="utf-8") as f:
                                    content = f.read()
                                # 隐藏API密钥
                                hidden_content = content.replace(dashscope_api_key, f"{dashscope_api_key[:4]}...{dashscope_api_key[-4:]}")
                                self.print_info(f".env文件内容:\n{hidden_content}")
                            else:
                                self.print_error(".env文件创建失败")
                            
                            self.print_success("API密钥配置成功！")
                            # 重新加载环境变量
                            load_dotenv()
                            
                            # 重新导入qwen模块，确保_CLIENT被重新初始化
                            self.print_info("正在重新初始化API客户端...")
                            if 'qwen' in sys.modules:
                                del sys.modules['qwen']
                            # 重新导入
                            from qwen import _CLIENT, _CLIENT_PROVIDER
                            self.print_info(f"重新初始化后，客户端状态: {_CLIENT is not None}")
                            if _CLIENT is not None:
                                self.print_info(f"客户端提供商: {_CLIENT_PROVIDER}")
                            # 打印更多调试信息
                            import os
                            dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
                            self.print_info(f"DASHSCOPE_API_KEY存在: {dashscope_api_key is not None}")
                            if dashscope_api_key:
                                self.print_info(f"DASHSCOPE_API_KEY长度: {len(dashscope_api_key)}")
                            
                            # 重新检查API密钥
                            dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
                            self.print_info(f"重新检查API密钥: {dashscope_api_key is not None}")
                            if dashscope_api_key:
                                hidden_key = f"{dashscope_api_key[:4]}...{dashscope_api_key[-4:]}"
                                self.print_info(f"API密钥: {hidden_key}")
                        except Exception as e:
                            self.print_error(f"写入.env文件失败: {e}")
                            # 尝试使用绝对路径
                            try:
                                import tempfile
                                temp_env_file = os.path.join(tempfile.gettempdir(), "fastapi1w1.env")
                                with open(temp_env_file, "w", encoding="utf-8") as f:
                                    f.write(f"DASHSCOPE_API_KEY={dashscope_api_key}\n")
                                self.print_info(f"已将API密钥写入临时文件: {temp_env_file}")
                                self.print_info("请手动复制此文件到项目根目录并重命名为.env")
                            except Exception as e2:
                                self.print_error(f"写入临时文件也失败: {e2}")
                    else:
                        self.print_error("API密钥输入为空")
                except Exception as e:
                    self.print_error(f"读取API密钥失败: {e}")
            
            # 再次检查API密钥
            dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
            
            # 检查qwen模块是否已经导入，如果没有，重新导入
            if 'qwen' not in sys.modules:
                self.print_info("重新导入qwen模块...")
                from qwen import _CLIENT, _CLIENT_PROVIDER
            
            # 检查API配置
            if _CLIENT is not None:
                if dashscope_api_key:
                    # 隐藏中间部分，只显示前4位和后4位
                    hidden_key = f"{dashscope_api_key[:4]}...{dashscope_api_key[-4:]}"
                    self.print_success(f"千问API已配置 (提供商: {_CLIENT_PROVIDER}, 密钥: {hidden_key})")
                else:
                    self.print_success(f"千问API已配置 (提供商: {_CLIENT_PROVIDER})")
                api_configured = True
            else:
                # 如果_CLIENT仍然为None，但dashscope_api_key存在，尝试手动初始化
                if dashscope_api_key:
                    self.print_info("尝试手动初始化API客户端...")
                    try:
                        from openai import OpenAI
                        base_url = os.getenv("DASHSCOPE_BASE_URL")
                        if base_url:
                            _CLIENT = OpenAI(api_key=dashscope_api_key, base_url=base_url)
                            _CLIENT_PROVIDER = "dashscope"
                        else:
                            _CLIENT = OpenAI(api_key=dashscope_api_key)
                            _CLIENT_PROVIDER = "openai"
                        hidden_key = f"{dashscope_api_key[:4]}...{dashscope_api_key[-4:]}"
                        self.print_success(f"千问API已配置 (提供商: {_CLIENT_PROVIDER}, 密钥: {hidden_key})")
                        api_configured = True
                    except Exception as e:
                        self.print_error(f"手动初始化API客户端失败: {e}")
                        api_configured = False
                else:
                    self.print_error("千问API未配置")
                    api_configured = False
            
            # 检查DASHSCOPE_API_KEY是否存在（用于TTS）
            if not dashscope_api_key:
                self.print_error("千问TTS API未配置")
                api_configured = False
            else:
                self.print_success("千问TTS API已配置")
            
            # 如果API未配置，显示配置指南
            if not api_configured:
                self.print_info("请先配置千问API密钥后再启动服务")
                self.print_info("")
                self.print_info("配置方法：")
                self.print_info("  方法1: 手动配置")
                self.print_info("    1. 复制 .env.example 为 .env")
                self.print_info("    2. 编辑 .env 文件，填入以下配置：")
                self.print_info("       - DASHSCOPE_API_KEY：千问API密钥")
                self.print_info("")
                self.print_info("  方法2: 下次启动时在控制台直接输入API密钥")
                self.print_info("")
                self.print_info("获取API密钥的方法：")
                self.print_info("  千问API密钥：")
                self.print_info("     - 访问：https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen")
                self.print_info("     - 按照指南获取API密钥")
                self.print_info("")
                self.print_info("注意：千问API密钥将用于对话生成和语音合成功能")
                
                return False
            
            return True
        except Exception as e:
            self.print_error(f"检查API配置失败: {e}")
            return False

    def start(self, foreground: bool = False, install_deps: bool = True, force: bool = False, monitor: bool = False):
        """启动应用"""
        # 检查API配置
        if not self._check_api_config():
            return False
        # 避免多实例：先检查 PID 文件与端口占用
        # 如果 PID 文件存在但端口未被占用，认为是过期 PID 文件，自动清理并继续启动
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    content = f.read().strip()
                    _ = int(content)
            except Exception:
                # 无效内容，清理
                try:
                    self.pid_file.unlink(missing_ok=True)
                    self.print_info("检测到无效的 PID 文件，已清理")
                except Exception:
                    pass
            else:
                # 有 PID 文件且内容看起来是数字，检查实际运行与端口占用
                if not self.is_running() and not self._is_port_in_use():
                    try:
                        self.pid_file.unlink(missing_ok=True)
                        self.print_info("已清理过期的 PID 文件")
                    except Exception:
                        pass

        if self.is_running():
            self.print_success("应用已在运行")
            self.print_info("访问地址: http://localhost:914")
            return True

        if self._is_port_in_use():
            if force:
                pid = self._get_pid_by_port(4190)
                if pid:
                    try:
                        if platform.system() == 'Windows':
                            subprocess.run(f"taskkill /PID {pid} /F", shell=True)
                        else:
                            os.kill(pid, signal.SIGKILL)
                        self.print_info(f"已终止进程 PID={pid}")
                        time.sleep(1)
                    except Exception as e:
                        self.print_error(f"终止进程失败: {e}")
                        return False
                else:
                    self.print_error("无法定位占用端口的进程")
                    return False
            else:
                self.print_error("端口 4190 已被占用")
                return False
            
        # 初始化步骤提示
        self.print_info("正在启动应用...")
        init_steps = ["检查依赖", "启动服务"]
        # Step 1: 检查依赖文件
        self._print_progress(1, len(init_steps), init_steps[0])

        # 每次启动进行一次环境检测；默认自动安装/修复缺失包，可通过 --no-install-deps 禁用
        requirements_file = self.project_root / "requirements.txt"
        if install_deps and requirements_file.exists():
            # 检测依赖并在内部输出是否需要安装/修复
            self._install_missing_requirements(requirements_file)
        else:
            self.print_info("跳过依赖检查")

        # Step 2: 准备启动
        self._print_progress(2, len(init_steps), init_steps[1])
        
        # 启动应用
        os.chdir(self.app_dir)
        
        # 使用uvicorn启动FastAPI应用
        # 确保 uvicorn 可用，否则尝试安装
        # 延迟导入并在缺失时提示（不自动安装），减少启动时的外部行为
        try:
            import uvicorn  # noqa: F401
        except ModuleNotFoundError:
            if install_deps:
                self.print_info("正在安装 uvicorn[standard]...")
                subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-warn-script-location", "--progress-bar", "on", "uvicorn[standard]"])
            else:
                self.print_error("未找到 uvicorn，请运行 'python run.py start --install-deps'")
                return False

        try:
            import fastapi  # noqa: F401
        except ModuleNotFoundError:
            if install_deps:
                self.print_info("正在安装 fastapi...")
                subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--no-warn-script-location", "--progress-bar", "on", "fastapi"])
            else:
                self.print_error("未找到 fastapi，请运行 'python run.py start --install-deps'")
                return False
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "4190"
        ]
        
        # 根据模式选择启动方式
        if foreground:
            # 在前台运行 uvicorn（阻塞当前进程），便于在终端直接停止
            try:
                import uvicorn
                self.print_info("前台模式启动 (按 Ctrl+C 停止)")
                uvicorn.run("main:app", host="0.0.0.0", port=4190)
                return True
            except Exception as e:
                self.print_error(f"启动失败: {e}")
                return False

        # 后台以子进程方式启动 uvicorn
        if platform.system() == "Windows":
            import subprocess as sp
            logfh = open(self.log_file, 'a', encoding='utf-8', errors='replace')
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            process = sp.Popen(
                cmd,
                stdout=logfh,
                stderr=sp.STDOUT,
                creationflags=sp.CREATE_NEW_PROCESS_GROUP,
                env=env
            )
        else:
            import subprocess as sp
            logfh = open(self.log_file, 'a', encoding='utf-8', errors='replace')
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            process = sp.Popen(
                cmd,
                stdout=logfh,
                stderr=sp.STDOUT,
                preexec_fn=os.setpgrp,
                env=env
            )
        
        # 保存PID
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        try:
            # 不再持有 logfh 引用会在子进程继承句柄后安全关闭父进程的文件描述符
            logfh.close()
        except Exception:
            pass

        # 在监控模式下：简化为直接等待子进程退出并在控制台打印退出提示
        if monitor:
            try:
                self.print_info(f"监控进程 PID={process.pid}")
                try:
                    exit_code = process.wait()
                except KeyboardInterrupt:
                    # 若用户按 Ctrl+C，提示并继续等待子进程退出
                    self.print_info("收到中断信号，等待进程退出...")
                    exit_code = process.wait()

                # 清理 pid 与浏览器标记
                try:
                    if self.pid_file.exists():
                        self.pid_file.unlink(missing_ok=True)
                except Exception:
                    pass

                if exit_code == 0:
                    self.print_success(f"进程正常退出 (PID={process.pid})")
                else:
                    self.print_warning(f"进程异常退出 (PID={process.pid}, code={exit_code})")
                return True
            except Exception as e:
                self.print_error(f"监控进程时出错: {e}")
                return False

        # 默认行为：等待端口就绪后检查是否启动成功
        self.print_info("等待服务启动...")
        
        # 等待端口就绪，最多等待30秒
        max_wait = 30
        for i in range(max_wait):
            if self._is_port_in_use("127.0.0.1", 4190):
                self.print_success(f"服务已就绪 ({i+1}s)")
                break
            time.sleep(1)
        else:
            self.print_error(f"等待 {max_wait} 秒后服务仍未就绪")
            return False

        if self.is_running():
            self.print_success("应用启动成功")
            url = "http://localhost:4190"
            self.print_info(f"访问地址: {url}")
            self.print_info(f"API 文档: {url}/docs")
            self.print_info(f"进程 PID: {process.pid}")
            self.print_info(f"日志文件: {self.log_file}")
            self.print_info("使用 'python run.py stop' 停止服务")
            return True
        else:
            self.print_error("应用启动失败，请检查日志")
            return False
    
    def stop(self):
        """停止应用"""
        self.print_info("正在停止应用...")
        
        # 步骤1: 尝试通过PID文件停止进程
        stopped_by_pid = False
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                self.print_info(f"停止进程 PID={pid}...")
                
                if platform.system() == "Windows":
                    # 在Windows上，使用taskkill强制终止进程树
                    result = subprocess.run(
                        ["taskkill", "/PID", str(pid), "/F", "/T"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        self.print_info(f"已终止进程 PID={pid}")
                        stopped_by_pid = True
                    else:
                        self.print_warning(f"终止进程失败: {result.stderr}")
                else:
                    # 在Unix系统上，尝试终止进程组
                    try:
                        os.killpg(pid, signal.SIGTERM)
                        self.print_info(f"已发送终止信号到进程组 PID={pid}")
                        stopped_by_pid = True
                    except ProcessLookupError:
                        self.print_warning(f"进程 PID={pid} 不存在")
                    except Exception as e:
                        self.print_warning(f"终止进程失败: {e}")
            except (ValueError, FileNotFoundError) as e:
                self.print_warning(f"读取 PID 文件失败: {e}")
            except Exception as e:
                self.print_warning(f"停止进程时出错: {e}")
        
        # 步骤2: 检查端口是否还被占用，如果是，则查找并终止占用端口的进程
        if self._is_port_in_use("127.0.0.1", 914):
            self.print_info("端口 914 仍被占用")
            port_pid = self._get_pid_by_port(914)
            
            if port_pid:
                self.print_info(f"终止占用端口的进程 PID={port_pid}")
                
                if platform.system() == "Windows":
                    result = subprocess.run(
                        ["taskkill", "/PID", str(port_pid), "/F", "/T"],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        self.print_info(f"已终止进程 PID={port_pid}")
                    else:
                        self.print_warning(f"终止进程失败: {result.stderr}")
                else:
                    try:
                        os.kill(port_pid, signal.SIGKILL)
                        self.print_info(f"已强制终止进程 PID={port_pid}")
                    except Exception as e:
                        self.print_warning(f"终止进程失败: {e}")
            else:
                self.print_warning("无法找到占用端口的进程")
        
        # 步骤3: 等待端口释放
        self.print_info("等待端口释放...")
        max_wait = 10
        for i in range(max_wait):
            if not self._is_port_in_use("127.0.0.1", 914):
                self.print_success(f"端口已释放 ({i+1}s)")
                break
            time.sleep(1)
        else:
            self.print_warning(f"等待 {max_wait} 秒后端口仍未释放")
        
        # 步骤4: 清理PID文件和浏览器标记
        try:
            if self.pid_file.exists():
                self.pid_file.unlink(missing_ok=True)
                self.print_info("已清理 PID 文件")
        except Exception as e:
            self.print_warning(f"清理 PID 文件失败: {e}")
        
        # 步骤4: 最终检查
        if self._is_port_in_use("127.0.0.1", 914):
            self.print_error("应用停止失败，端口仍被占用")
            self.print_info("运行 'netstat -ano | findstr :914' 查看占用进程")
            return False
        else:
            self.print_success("应用已停止")
            return True
    
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
            self.print_info("访问地址: http://localhost:914")
        else:
            self.print_info("应用未运行")
    
    def show_usage(self):
        """显示使用说明"""
        print("播客对话生成器")
        print("=" * 40)
        print("用法: python run.py <命令>")
        print()
        print("命令:")
        print("  start    启动应用")
        print("  stop     停止应用")
        print("  restart  重启应用")
        print("  status   查看状态")
        print("  logs     查看日志")

def main():
    parser = argparse.ArgumentParser(description="管理播客对话生成器服务")
    parser.add_argument('command', choices=['start', 'stop', 'restart', 'status', 'logs'], help='命令')

    parser.add_argument('--foreground', action='store_true', help='在前台运行（不以子进程）')
    # 自动安装缺失依赖（默认开启）。如需禁用，请使用 --no-install-deps
    install_group = parser.add_mutually_exclusive_group()
    install_group.add_argument('--install-deps', dest='install_deps', action='store_true', help='启动时安装/修复缺失依赖（默认）')
    install_group.add_argument('--no-install-deps', dest='install_deps', action='store_false', help='启动时不自动安装缺失依赖')
    parser.set_defaults(install_deps=True)
    parser.add_argument('--force', action='store_true', help='当端口被占用时强制结束占用进程并启动')
    monitor_group = parser.add_mutually_exclusive_group()
    monitor_group.add_argument('--monitor', dest='monitor', action='store_true', help='启动后在父进程中监控后端，后端退出时在控制台输出提示')
    monitor_group.add_argument('--no-monitor', dest='monitor', action='store_false', help='不在父进程中监控后端（后台模式）')
    parser.set_defaults(monitor=False)
    args = parser.parse_args()

    manager = FastAPIManager()
    command = args.command.lower()

    if command == 'start':
        success = manager.start(foreground=args.foreground, install_deps=args.install_deps, force=args.force, monitor=args.monitor)
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
# 添加命令行入口函数
def start_command():
    """命令行入口：启动应用"""
    manager = FastAPIManager()
    success = manager.start()
    sys.exit(0 if success else 1)

def stop_command():
    """命令行入口：停止应用"""
    manager = FastAPIManager()
    success = manager.stop()
    sys.exit(0 if success else 1)

def restart_command():
    """命令行入口：重启应用"""
    manager = FastAPIManager()
    success = manager.restart()
    sys.exit(0 if success else 1)

def status_command():
    """命令行入口：查看状态"""
    manager = FastAPIManager()
    manager.status()

def logs_command():
    """命令行入口：查看日志"""
    manager = FastAPIManager()
    if manager.log_file.exists():
        try:
            if platform.system() == "Windows":
                subprocess.run(["powershell", "-Command", f"Get-Content {manager.log_file} -Wait -Tail 20"])
            else:
                subprocess.run(["tail", "-f", str(manager.log_file)])
        except KeyboardInterrupt:
            print("\n停止查看日志")
    else:
        print("日志文件不存在")

def init_venv_command():
    """命令行入口：初始化虚拟环境"""
    manager = FastAPIManager()
    success = manager.init_virtualenv()
    sys.exit(0 if success else 1)
    
if __name__ == "__main__":
    main()