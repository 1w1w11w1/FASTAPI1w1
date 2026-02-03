# 播客对话生成器

基于 FastAPI 的播客式对话生成器，提供完整的服务管理方案，支持跨平台运行。

## 目录

- [项目简介](#项目简介)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [API配置](#api配置)
- [服务管理](#服务管理)
- [命令参数](#命令参数)
- [故障排查](#故障排查)
- [开发调试](#开发调试)
- [文件说明](#文件说明)

## 项目简介

这是一个基于 FastAPI 构建的播客式对话生成器，提供以下特性：

- 完整的服务管理脚本（启动、停止、重启、状态监控）
- 自动依赖检测与安装
- 单实例控制，确保同时只有一个实例运行
- 跨平台支持（Windows/Linux/macOS）
- 详细的日志记录
- 简洁的命令行界面
- 支持千问/OpenAI API

### 核心文件

- `run.py` - 服务管理主脚本
- `app/main.py` - FastAPI 后端主程序
- `app/qwen.py` - 对话生成逻辑
- `requirements.txt` - Python 依赖清单
- `logs/app.log` - 运行时日志
- `app/static/html/index.html` - 前端页面

## 环境要求

- **Python**: 3.8 或更高版本（推荐 3.11）
- **操作系统**: Windows / Linux / macOS
- **磁盘空间**: 至少 100MB 可用空间
- **内存**: 建议 512MB 以上

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

#### 方法1：使用配置脚本（推荐）

```bash
python setup_api.py
```

按照提示选择API类型并输入密钥即可。

#### 方法2：手动配置

复制 `.env.example` 为 `.env` 并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的API密钥：

```env
# 阿里云千问（推荐）
DASHSCOPE_API_KEY=your-dashscope-api-key-here
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 或使用OpenAI兼容接口
OPENAI_API_KEY=your-openai-api-key-here
```

#### 方法3：环境变量

**Windows PowerShell**:
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

**Linux/macOS**:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 启动服务

```bash
python run.py start
```

### 4. 访问应用

启动成功后，在浏览器中打开以下地址：

- **主页面**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## API配置

### 支持的API

#### 1. 阿里云千问（推荐）

**获取API密钥**:
1. 访问 [阿里云控制台](https://dashscope.console.aliyun.com/)
2. 开通千问服务
3. 创建API-KEY

**配置方式**:
```env
DASHSCOPE_API_KEY=your-dashscope-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

#### 2. OpenAI兼容接口

支持任何兼容OpenAI格式的API服务。

**配置方式**:
```env
OPENAI_API_KEY=your-api-key
```

### 配置参数

| 参数 | 默认值 | 说明 |
|------|---------|------|
| MODEL | qwen-plus | 使用的模型 |
| MAX_TOKENS | 4096 | 最大输出token数 |
| TEMPERATURE | 0.7 | 创造性（0-1） |

### 验证配置

```bash
python check_api.py
```

预期输出:

```
==================================================
千问API配置检查
==================================================
状态: 已配置
提供商: openai
Client: <openai.OpenAI object>
==================================================
```

## 服务管理

### 启动服务

```bash
python run.py start
```

**特性**：
- 自动检查并安装缺失的依赖
- 单实例控制：如果应用已在运行，会显示访问地址并退出
- 默认后台运行，不阻塞控制台
- 自动清理过期的 PID 文件

### 停止服务

```bash
python run.py stop
```

**特性**：
- 优雅终止进程
- 自动清理 PID 文件
- 等待端口释放
- 支持强制终止占用端口的进程

### 重启服务

```bash
python run.py restart
```

**特性**：
- 先停止现有服务
- 等待 2 秒
- 重新启动服务

### 查看服务状态

```bash
python run.py status
```

**输出示例**：

```
应用正在运行 (PID: 12345)
访问地址: http://localhost:8000
```

或

```
应用未运行
```

### 查看实时日志

**Windows PowerShell**:
```bash
python run.py logs
# 或直接查看日志文件
Get-Content logs\app.log -Wait -Tail 20
```

**Linux/macOS**:
```bash
tail -f logs/app.log
```

## 命令参数

### start 命令参数

```bash
python run.py start [选项]
```

**可用选项**：

| 参数 | 说明 |
|------|------|
| `--foreground` | 前台运行（直接输出日志，Ctrl+C 停止） |
| `--no-install-deps` | 跳过依赖检查和自动安装 |
| `--install-deps` | 强制检查并安装缺失依赖（默认行为） |
| `--force` | 强制结束占用端口的进程并启动 |
| `--monitor` | 监控模式，阻塞控制台直到后端退出 |
| `--no-monitor` | 后台模式，不阻塞控制台（默认行为） |

### 使用示例

```bash
# 默认启动（后台运行）
python run.py start

# 前台运行（实时查看日志）
python run.py start --foreground

# 跳过依赖检查
python run.py start --no-install-deps

# 强制启动（结束占用端口的进程）
python run.py start --force

# 监控模式（阻塞控制台）
python run.py start --monitor
```

## 故障排查

### 常见问题

#### 1. 端口 8000 被占用

**症状**：
```
端口 8000 已被占用
```

**Windows 解决方案**：

```bash
# 查看占用进程
netstat -ano | findstr :8000

# 查看进程详情
tasklist /FI "PID eq <PID>"

# 强制结束进程
taskkill /PID <PID> /F

# 或使用强制启动
python run.py start --force
```

**Linux/macOS 解决方案**：

```bash
# 查看占用进程
lsof -i :8000

# 结束进程
kill -9 <PID>
```

#### 2. PID 文件存在但服务未运行

**症状**：
```
应用未运行
```

**解决方案**：

```bash
# 脚本会自动清理无效 PID 文件
# 如需手动清理：
Remove-Item app.pid -Force  # Windows
rm app.pid  # Linux/macOS
```

#### 3. 依赖安装失败

**症状**：
```
安装失败: <package-name>
```

**解决方案**：

```bash
# 检查网络连接
# 验证 requirements.txt 格式
# 尝试手动安装
python -m pip install -r requirements.txt

# 使用国内镜像源（可选）
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 4. API未配置

**症状**：
```
Qwen/OpenAI client 未配置（请设置 OPENAI_API_KEY 或 DASHSCOPE_API_KEY）
```

**解决方案**：

```bash
# 使用配置脚本
python setup_api.py

# 或手动配置
cp .env.example .env
# 编辑 .env 文件，填入API密钥
```

#### 5. 服务启动失败

**症状**：
```
应用启动失败，请检查日志
```

**解决方案**：

```bash
# 查看详细日志
Get-Content logs\app.log  # Windows
cat logs/app.log  # Linux/macOS

# 检查端口是否被占用
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/macOS

# 尝试前台运行查看错误
python run.py start --foreground
```

#### 6. 应用已在运行

**症状**：
```
应用已在运行
访问地址: http://localhost:8000
```

**说明**：
- 这是正常行为，表示单实例控制正在工作
- 不会启动新的实例
- 可以直接访问显示的地址

## 开发调试

### 调试模式

```bash
# 前台运行，实时查看日志
python run.py start --foreground

# 监控模式，阻塞控制台
python run.py start --monitor
```

### 日志级别调整

编辑 `app/main.py` 中的日志配置，修改日志级别以获取更详细的信息。

### 前端修改

- **前端页面**: `app/static/html/index.html`
- **静态资源**: `app/static/` 目录
- **修改后需重启服务生效**

```bash
python run.py restart
```

## 文件说明

### 关键文件

| 文件路径 | 说明 |
|---------|------|
| `run.py` | 主管理脚本，包含所有服务管理命令 |
| `app/main.py` | FastAPI 后端主程序，包含路由和业务逻辑 |
| `app/qwen.py` | 对话生成逻辑，调用千问/OpenAI API |
| `requirements.txt` | Python 依赖包列表 |
| `logs/app.log` | 运行时日志文件（自动生成） |
| `app.pid` | 进程 ID 记录文件（自动生成） |
| `app/static/html/index.html` | 前端主页面 |
| `.env.example` | API配置示例文件 |
| `.env` | API配置文件（用户创建） |
| `setup_api.py` | API配置向导脚本 |
| `check_api.py` | API配置检查脚本 |
| `tests/test_models.py` | 单个模型快速测试脚本 |
| `tests/compare_models.py` | 多模型全面对比测试脚本 |
| `tests/README.md` | 测试脚本使用说明 |

### 目录结构

```
项目根目录/
├── run.py              # 管理脚本
├── requirements.txt    # 依赖文件
├── .env.example        # API配置示例
├── .env               # API配置（用户创建）
├── setup_api.py       # 配置向导
├── check_api.py        # 配置检查
├── app/
│   ├── main.py        # 后端主程序
│   ├── qwen.py        # 对话生成逻辑
│   └── static/        # 静态资源
│       └── html/
│           └── index.html  # 前端页面
├── tests/             # 测试脚本目录
│   ├── test_models.py    # 单个模型测试
│   ├── compare_models.py # 多模型对比
│   ├── results/          # 测试结果（自动生成）
│   └── README.md         # 测试说明
└── logs/              # 日志目录
    └── app.log        # 运行日志
```

## 模型测试

### 快速测试

测试单个模型的对话生成效果：

```bash
cd tests
python test_models.py
```

**功能**：
- 测试所有可用的千问模型
- 使用相同的测试文本
- 显示每个模型的生成结果
- 推荐最佳模型

### 全面对比

对比多个模型在不同风格和场景下的表现：

```bash
cd tests
python compare_models.py
```

**功能**：
- 测试所有模型 × 所有风格 × 所有测试用例的组合
- 生成详细的对比报告
- 保存测试结果为JSON文件
- 生成可读性强的文本报告

### 查看测试结果

测试结果保存在 `tests/results/` 目录：

- `model_comparison.json` - 详细的JSON格式测试结果
- `comparison_report.txt` - 可读的文本格式报告

### 模型推荐

| 模型 | 适用场景 | 特点 | 推荐度 |
|------|---------|------|--------|
| **deepseek-v3.2** | 对话生成（推荐） | 深度优化版本，性能优秀，对话自然，综合评分最高 | ⭐⭐⭐⭐⭐ |
| **qwen-vl-max-2025-08-13** | 高质量对话生成 | 视觉语言模型，性能最强，支持多模态 | ⭐⭐⭐⭐ |
| **qwen-flash-character** | 快速测试 | 闪电版模型，速度快，成本低，适合快速验证 | ⭐⭐⭐ |

**测试结果总结**（2026-02-03）：
- **deepseek-v3.2**: 综合评分 68/70 - 对话段数丰富（8段），自然度满分
- **qwen-vl-max-2025-08-13**: 综合评分 64/70 - 对话质量高，段数适中（4段）
- **qwen-flash-character**: 综合评分 63/70 - 快速响应，但段数较少（4段）

**默认模型**: 已设置为 `deepseek-v3.2`（基于测试结果）

### 修改默认模型

测试完成后，根据结果选择最佳模型，修改 `app/qwen.py` 中的默认模型参数：

```python
def _call_qwen_api(prompt: str, system_prompt: str = None, model: str = "qwen-max", max_tokens: int = 4096) -> str:
    # 修改 model 参数为测试后选择的最佳模型
```

详细说明请查看 [tests/README.md](tests/README.md)

## 获取帮助

如遇本手册未涵盖的问题：

1. 查看 `logs/app.log` 获取详细错误信息
2. 检查 Python 环境：`python --version`
3. 确保所有依赖已安装：`pip list`
4. 验证API配置：`python check_api.py`
5. 在项目中提交 Issue 或联系开发者

## 更新记录

- **2026-02-02**: 
  - 移除自动关闭浏览器机制
  - 移除心跳机制
  - 优化单实例控制逻辑
  - 简化命令行参数
  - 改进输出提示信息
  - 默认后台运行，不阻塞控制台
  - 添加.env文件支持
  - 添加API配置向导
  - 优化token配置（4096）
  - 添加temperature参数（0.7）

## 注意事项

- 所有命令以 Windows PowerShell 为例，Linux/macOS 用户请使用对应命令
- 默认端口为 8000，如需修改请编辑 `app/main.py` 中的启动配置
- 应用支持单实例运行，重复启动不会创建新实例
- 日志文件会持续增长，建议定期清理
- API密钥请妥善保管，不要提交到代码仓库

## 许可证

本项目仅供学习和个人使用。
