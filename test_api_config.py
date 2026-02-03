import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 检查API配置
openai_key = os.getenv('OPENAI_API_KEY')
dashscope_key = os.getenv('DASHSCOPE_API_KEY')
dashscope_base_url = os.getenv('DASHSCOPE_BASE_URL')
model = os.getenv('MODEL', 'deepseek-v3.2')

print("API配置检查结果：")
print(f"OPENAI_API_KEY: {'已配置' if openai_key else '未配置'}")
print(f"DASHSCOPE_API_KEY: {'已配置' if dashscope_key else '未配置'}")
print(f"DASHSCOPE_BASE_URL: {dashscope_base_url}")
print(f"使用的模型: {model}")

# 尝试创建OpenAI客户端
if openai_key or dashscope_key:
    try:
        from openai import OpenAI
        
        api_key = dashscope_key or openai_key
        base_url = dashscope_base_url
        
        if base_url:
            client = OpenAI(api_key=api_key, base_url=base_url)
            print("使用阿里云千问API")
        else:
            client = OpenAI(api_key=api_key)
            print("使用OpenAI API")
        
        print("客户端创建成功！")
        print("API配置正常。")
    except Exception as e:
        print(f"客户端创建失败: {e}")
        print("API配置可能有问题。")
else:
    print("未配置API密钥。")
