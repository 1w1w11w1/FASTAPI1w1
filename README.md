# 播客对话生成器

基于 FastAPI 的播客式对话生成器，帮助你快速创建生动有趣的播客对话内容。

## 快速开启

### 1. 安装依赖

打开 Windows PowerShell，执行以下命令：

```powershell
pip install -r requirements.txt
```

如果遇到网络问题，可以使用国内镜像源：

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 配置API密钥

**推荐方法**：使用配置脚本

```powershell
python setup_api.py
```

按照提示选择API类型并输入密钥即可。

**备用方法**：手动配置

复制 `.env.example` 为 `.env` 并编辑，填入你的API密钥：

```env
# 阿里云千问（推荐）
DASHSCOPE_API_KEY=your-dashscope-api-key-here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 或使用OpenAI兼容接口
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. 启动服务

```powershell
python run.py start
```

启动成功后，在浏览器中打开以下地址：

- **主页面**: http://localhost:914
- **播客生成器**: http://localhost:914/podcast-generator

### 4. 使用方法

1. 在输入框中粘贴或输入你想要转换为播客对话的文本内容
2. 或点击"选择文件"按钮导入txt文件
3. 选择对话风格和参与者数量
4. 点击"生成播客对话"按钮
5. 等待生成完成，查看结果
6. 生成的对话会自动保存到result目录
7. 可以点击"导出为文本文件"或"导出为JSON文件"下载结果

## 常见问题排查

### 1. 端口 914 被占用

**症状**：启动时显示"端口 914 已被占用"

**解决方案**：

```powershell
# 查看占用进程
netstat -ano | findstr :914

# 查看进程详情
tasklist /FI "PID eq <PID>"

# 强制结束进程
taskkill /PID <PID> /F

# 或使用强制启动
python run.py start --force
```

### 2. API未配置

**症状**：启动时显示"Qwen/OpenAI client 未配置"

**解决方案**：

```powershell
# 使用配置脚本
python setup_api.py

# 或手动配置
# 复制 .env.example 为 .env 并编辑，填入API密钥
```

### 3. 依赖安装失败

**症状**：安装依赖时显示错误信息

**解决方案**：

```powershell
# 检查Python版本
python --version

# 升级pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 服务启动失败

**症状**：启动时显示"应用启动失败，请检查日志"

**解决方案**：

```powershell
# 查看详细日志
Get-Content logs\app.log

# 尝试前台运行查看错误
python run.py start --foreground

# 检查端口是否被占用
netstat -ano | findstr :914
```

### 5. 应用已在运行

**症状**：启动时显示"应用已在运行，访问地址: http://localhost:914"

**说明**：这是正常行为，表示单实例控制正在工作，不会启动新的实例，你可以直接访问显示的地址。

### 6. 文件导入失败

**症状**：点击"选择文件"后无法导入文本

**解决方案**：
- 确保文件格式为.txt
- 确保文件编码为UTF-8
- 确保文件大小适中（建议不超过10MB）

## 服务管理

### 基本命令

```powershell
# 启动服务
python run.py start

# 停止服务
python run.py stop

# 重启服务
python run.py restart

# 查看服务状态
python run.py status

# 查看日志
python run.py logs
```

### 启动选项

```powershell
# 前台运行（实时查看日志）
python run.py start --foreground

# 跳过依赖检查
python run.py start --no-install-deps

# 强制启动（结束占用端口的进程）
python run.py start --force
```

## 功能特性

- ✅ 支持输入文本或导入txt文件生成对话
- ✅ 自动保存生成的对话到result目录
- ✅ 显示token使用量，帮助你了解API调用消耗
- ✅ 支持导出为文本文件和JSON文件
- ✅ 提供多种对话风格选择
- ✅ 支持2-4人对话
- ✅ 单实例控制，确保系统稳定
- ✅ 详细的日志记录，便于排查问题

## 注意事项

- 请妥善保管你的API密钥，不要提交到代码仓库
- 默认端口为914，如需修改请编辑app/main.py文件
- 生成的对话会自动保存在result目录，文件名为对话内容的简短摘要
- 日志文件会持续增长，建议定期清理logs目录
- 本项目仅供学习和个人使用

## 获取帮助

如果遇到问题：

1. 查看 `logs/app.log` 获取详细错误信息
2. 检查 Python 版本：`python --version`
3. 确保所有依赖已安装：`pip list`
4. 验证API配置：`python check_api.py`
5. 参考本手册的"常见问题排查"部分