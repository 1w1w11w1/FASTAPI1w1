#!/usr/bin/env python3
"""
API配置脚本 - 简单设置千问/OpenAI API密钥
"""

import os
import sys
from pathlib import Path

def setup_api():
    """设置API密钥"""
    print("=" * 50)
    print("API配置向导")
    print("=" * 50)
    print()
    
    print("请选择API类型:")
    print("1. 阿里云千问 (推荐)")
    print("2. OpenAI兼容接口")
    print("3. 查看当前配置")
    print("0. 退出")
    print()
    
    choice = input("请输入选项 (0-3): ").strip()
    
    if choice == "0":
        print("已退出")
        return
    elif choice == "1":
        setup_dashscope()
    elif choice == "2":
        setup_openai()
    elif choice == "3":
        show_current_config()
    else:
        print("无效选项")
        return
    
    print()
    print("=" * 50)
    print("配置完成！")
    print("=" * 50)
    print()
    print("下一步:")
    print("1. 运行: python run.py start")
    print("2. 访问: http://localhost:914")
    print("3. 测试生成对话功能")

def setup_dashscope():
    """配置阿里云千问"""
    print()
    print("配置阿里云千问")
    print("-" * 30)
    print()
    
    api_key = input("请输入千问API密钥: ").strip()
    if not api_key:
        print("错误: API密钥不能为空")
        return
    
    # 写入.env文件
    env_file = Path(__file__).parent / ".env"
    
    env_content = f"""# 千问API配置
DASHSCOPE_API_KEY={api_key}
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL=qwen-plus
MAX_TOKENS=4096
TEMPERATURE=0.7
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"配置已保存到: {env_file}")
        print()
        print("配置内容:")
        print(f"  DASHSCOPE_API_KEY: {api_key[:8]}...")
        print(f"  DASHSCOPE_BASE_URL: https://dashscope.aliyuncs.com/compatible-mode/v1")
        print(f"  MODEL: qwen-plus")
        print(f"  MAX_TOKENS: 4096")
        print(f"  TEMPERATURE: 0.7")
    except Exception as e:
        print(f"错误: 保存配置失败 - {e}")

def setup_openai():
    """配置OpenAI兼容接口"""
    print()
    print("配置OpenAI兼容接口")
    print("-" * 30)
    print()
    
    api_key = input("请输入OpenAI API密钥: ").strip()
    if not api_key:
        print("错误: API密钥不能为空")
        return
    
    # 写入.env文件
    env_file = Path(__file__).parent / ".env"
    
    env_content = f"""# OpenAI API配置
OPENAI_API_KEY={api_key}
MODEL=qwen-plus
MAX_TOKENS=4096
TEMPERATURE=0.7
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"配置已保存到: {env_file}")
        print()
        print("配置内容:")
        print(f"  OPENAI_API_KEY: {api_key[:8]}...")
        print(f"  MODEL: qwen-plus")
        print(f"  MAX_TOKENS: 4096")
        print(f"  TEMPERATURE: 0.7")
    except Exception as e:
        print(f"错误: 保存配置失败 - {e}")

def show_current_config():
    """显示当前配置"""
    print()
    print("当前配置")
    print("-" * 30)
    print()
    
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("未找到 .env 配置文件")
        print()
        print("请先运行配置向导设置API密钥")
        return
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("配置文件内容:")
        print()
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    if 'KEY' in key:
                        masked = value[:8] + "..." if len(value) > 8 else "***"
                        print(f"  {key}: {masked}")
                    else:
                        print(f"  {key}: {value}")
    except Exception as e:
        print(f"错误: 读取配置失败 - {e}")

if __name__ == "__main__":
    try:
        setup_api()
    except KeyboardInterrupt:
        print()
        print("已取消")
    except Exception as e:
        print(f"错误: {e}")
