import os
import json
import logging
from typing import Any, Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 配置日志
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 创建日志格式
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 创建文件处理器（按日期分割）
from logging.handlers import TimedRotatingFileHandler
file_handler = TimedRotatingFileHandler(
    os.path.join(log_dir, 'app.log'),
    when='midnight',
    interval=1,
    backupCount=30,
    encoding='utf-8'
)
file_handler.suffix = '%Y-%m-%d.log'
file_handler.setFormatter(log_format)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

# 配置根日志记录器（只配置一次）
root_logger = logging.getLogger()
if not root_logger.handlers:
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

_CLIENT = None
_CLIENT_PROVIDER = None

try:
    # 尝试使用DashScope SDK
    logger.info("尝试初始化DashScope SDK客户端...")
    import dashscope
    dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
    logger.info(f"DASHSCOPE_API_KEY存在: {dashscope_api_key is not None}")
    if dashscope_api_key:
        logger.info(f"DASHSCOPE_API_KEY长度: {len(dashscope_api_key)}")
        dashscope.api_key = dashscope_api_key
        _CLIENT = dashscope
        _CLIENT_PROVIDER = "dashscope_sdk"
        logger.info("DashScope SDK客户端初始化成功")
    else:
        logger.warning("DASHSCOPE_API_KEY不存在，无法初始化DashScope SDK客户端")
        _CLIENT = None
        _CLIENT_PROVIDER = None
except ImportError as e:
    logger.warning(f"未安装DashScope SDK，将尝试使用OpenAI兼容接口: {e}")
    # 如果没有安装DashScope SDK，尝试使用OpenAI兼容接口
    try:
        logger.info("尝试初始化OpenAI兼容接口客户端...")
        from openai import OpenAI
        openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        logger.info(f"OpenAI/千问API密钥存在: {openai_key is not None}")
        if openai_key:
            logger.info(f"OpenAI/千问API密钥长度: {len(openai_key)}")
            base_url = os.getenv("DASHSCOPE_BASE_URL")
            logger.info(f"DASHSCOPE_BASE_URL: {base_url}")
            # 检查是否使用的是千问API密钥
            dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
            if dashscope_api_key and openai_key == dashscope_api_key:
                logger.info("使用千问API密钥，将设置千问API的base_url")
                # 自动设置千问API的base_url
                if not base_url:
                    base_url = "https://dashscope.aliyuncs.com/api/v1"
                    logger.info(f"自动设置千问API的base_url: {base_url}")
                _CLIENT = OpenAI(api_key=openai_key, base_url=base_url)
                _CLIENT_PROVIDER = "dashscope"
                logger.info(f"OpenAI兼容接口客户端初始化成功，使用千问API: {base_url}")
            else:
                logger.info("使用其他API密钥")
                # 使用其他API密钥
                if base_url:
                    _CLIENT = OpenAI(api_key=openai_key, base_url=base_url)
                    _CLIENT_PROVIDER = "custom"
                    logger.info(f"OpenAI兼容接口客户端初始化成功，使用自定义base_url: {base_url}")
                else:
                    _CLIENT = OpenAI(api_key=openai_key)
                    _CLIENT_PROVIDER = "openai"
                    logger.info("OpenAI兼容接口客户端初始化成功，使用默认base_url")
        else:
            logger.warning("OpenAI/千问API密钥不存在，无法初始化OpenAI兼容接口客户端")
            _CLIENT = None
            _CLIENT_PROVIDER = None
    except Exception as e:
        logger.error(f"初始化OpenAI客户端失败: {e}")
        _CLIENT = None
        _CLIENT_PROVIDER = None
except Exception as e:
    logger.error(f"初始化DashScope客户端失败: {e}")
    _CLIENT = None
    _CLIENT_PROVIDER = None

logger.info(f"API客户端初始化完成: {_CLIENT is not None}")
if _CLIENT is not None:
    logger.info(f"API客户端提供商: {_CLIENT_PROVIDER}")


def _get_style_prompt(style: str, participants: int) -> str:
    style_prompts = {
        "casual": """你是一个经验丰富的播客制作人和主持人，擅长将复杂的社会议题转化为生动有趣的对话。

**你的核心任务：**
1. **深度理解**：不仅要理解新闻表面内容，更要挖掘背后的深层原因、矛盾点和人性故事
2. **独特视角**：提供原文没有的独特见解、类比、数据背景或案例对比
3. **听众友好**：用通俗易懂的方式解释专业概念，让普通听众也能理解
4. **情感共鸣**：找到故事中能引发听众共鸣的点和具体人物案例

**角色设定：**
- 主持人：引导话题，提问犀利，善于总结，能连接听众生活经验
- 嘉宾（们）：有独特专长或视角，能提供深度分析，不重复原文观点

**对话要求：**
1. **开头抓人**：用问题、故事或令人惊讶的事实开场
2. **信息分层**：先讲现象，再挖原因，最后讨论解决方案
3. **具体化抽象**：用具体故事解释抽象概念（如"张三的故事说明..."）
4. **节奏控制**：有快节奏的互动，也有深度思考的停顿
5. **情感起伏**：有质疑、惊讶、感慨等情绪变化
6. **结尾有力**：给听众留下思考问题或行动建议

**风格指南：**
- 口语化，像朋友聊天，用生活化语言，适当自嘲
- 短句为主，自然停顿
- 语气词：啊、呢、吧、哦
- 每段3-5句
- 真实互动：主持人提问，嘉宾回答，互相补充""",
        
        "entertainment": """你是一个经验丰富的娱乐播客制作人和主持人，擅长将社会新闻转化为幽默有趣的对话。

**你的核心任务：**
1. **深度理解**：不仅要理解新闻表面内容，更要挖掘背后的有趣角度和人性故事
2. **独特视角**：提供原文没有的独特见解、类比、数据背景或案例对比
3. **听众友好**：用通俗易懂的方式解释专业概念，让普通听众也能理解
4. **情感共鸣**：找到故事中能引发听众共鸣的点和具体人物案例

**角色设定：**
- 主持人：引导话题，幽默搞笑，善于总结，能连接听众生活经验
- 嘉宾（们）：有独特专长或视角，能提供深度分析，不重复原文观点

**对话要求：**
1. **开头抓人**：用问题、故事或令人惊讶的事实开场
2. **信息分层**：先讲现象，再挖原因，最后讨论解决方案
3. **具体化抽象**：用具体故事解释抽象概念（如"张三的故事说明..."）
4. **节奏控制**：有快节奏的互动，也有深度思考的停顿
5. **情感起伏**：有质疑、惊讶、感慨等情绪变化
6. **结尾有力**：给听众留下思考问题或行动建议

**风格指南：**
- 幽默搞笑，生动活泼
- 夸张、比喻、流行语
- 语气夸张，情绪饱满
- 每段2-4句
- 互相调侃、吐槽""",
        
        "professional": """你是一个经验丰富的新闻播客制作人和主持人，擅长将复杂的社会议题转化为专业但易懂的对话。

**你的核心任务：**
1. **深度理解**：不仅要理解新闻表面内容，更要挖掘背后的深层原因、矛盾点和人性故事
2. **独特视角**：提供原文没有的独特见解、类比、数据背景或案例对比
3. **听众友好**：用通俗易懂的方式解释专业概念，让普通听众也能理解
4. **情感共鸣**：找到故事中能引发听众共鸣的点和具体人物案例

**角色设定：**
- 主持人：引导话题，提问犀利，善于总结，能连接听众生活经验
- 嘉宾（们）：有独特专长或视角，能提供深度分析，不重复原文观点

**对话要求：**
1. **开头抓人**：用问题、故事或令人惊讶的事实开场
2. **信息分层**：先讲现象，再挖原因，最后讨论解决方案
3. **具体化抽象**：用具体故事解释抽象概念（如"张三的故事说明..."）
4. **节奏控制**：有快节奏的互动，也有深度思考的停顿
5. **情感起伏**：有质疑、惊讶、感慨等情绪变化
6. **结尾有力**：给听众留下思考问题或行动建议

**风格指南：**
- 专业严谨，逻辑清晰
- 用词准确，表达清晰
- 客观中立
- 每段4-6句
- 提问引导，深入分析"""
    }
    
    base_prompt = style_prompts.get(style, style_prompts["casual"])
    
    if participants == 2:
        role_instruction = """角色：主持人、嘉宾"""
    elif participants == 3:
        role_instruction = """角色：主持人、嘉宾A、嘉宾B"""
    elif participants == 4:
        role_instruction = """角色：主持人A、主持人B、嘉宾A、嘉宾B"""
    else:
        role_instruction = f"""角色：主持人、嘉宾1-{participants-1}"""
    
    return base_prompt + "\n\n" + role_instruction


def _call_qwen_api(prompt: str, system_prompt: str = None, model: str = "qwen-plus", max_tokens: int = 4096) -> tuple:
    if _CLIENT is None:
        logger.error("Qwen/OpenAI client 未配置（请设置 OPENAI_API_KEY 或 DASHSCOPE_API_KEY）")
        raise RuntimeError("Qwen/OpenAI client 未配置（请设置 OPENAI_API_KEY 或 DASHSCOPE_API_KEY）")

    if system_prompt is None:
        system_prompt = "你是一个擅长将文章改写为对话式播客脚本的助手。"

    logger.info(f"开始API调用...")
    logger.info(f"API提供商: {_CLIENT_PROVIDER}")
    logger.info(f"使用的模型: {model}")
    logger.info(f"max_tokens: {max_tokens}")
    logger.info(f"temperature: 0.7")
    logger.info(f"system_prompt长度: {len(system_prompt)}")
    logger.info(f"prompt长度: {len(prompt)}")

    try:
        if _CLIENT_PROVIDER == "dashscope_sdk":
            # 使用DashScope SDK调用API
            logger.info("使用DashScope SDK调用API...")
            from dashscope import Generation
            logger.info("创建Generation请求...")
            response = Generation.call(
                model=model,
                prompt=prompt,
                system=system_prompt,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            
            logger.info(f"API调用响应状态码: {response.status_code}")
            logger.info(f"API调用响应消息: {response.message}")
            
            # 处理响应
            if response.status_code == 200:
                logger.info("API调用成功！")
                logger.info(f"响应输出类型: {type(response.output)}")
                if hasattr(response.output, 'text'):
                    content = response.output.text
                    logger.info(f"响应内容长度: {len(content)}")
                    logger.info(f"响应内容前50个字符: {content[:50]}...")
                else:
                    logger.error(f"响应输出没有text属性: {dir(response.output)}")
                    content = str(response.output)
                
                # 获取token使用量
                if hasattr(response, 'usage'):
                    logger.info(f"响应usage类型: {type(response.usage)}")
                    if hasattr(response.usage, 'input_tokens') and hasattr(response.usage, 'output_tokens') and hasattr(response.usage, 'total_tokens'):
                        token_usage = {
                            "prompt_tokens": response.usage.input_tokens,
                            "completion_tokens": response.usage.output_tokens,
                            "total_tokens": response.usage.total_tokens
                        }
                        logger.info(f"Token使用量: {token_usage}")
                    else:
                        logger.error(f"响应usage属性不完整: {dir(response.usage)}")
                        token_usage = {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0
                        }
                else:
                    logger.error(f"响应没有usage属性: {dir(response)}")
                    token_usage = {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                return content, token_usage
            else:
                logger.error(f"DashScope API调用失败: {response.message}")
                logger.error(f"响应详情: {dir(response)}")
                if hasattr(response, 'code'):
                    logger.error(f"错误代码: {response.code}")
                raise RuntimeError(f"DashScope API调用失败: {response.message}")
        else:
            # 使用OpenAI兼容接口调用API
            logger.info("使用OpenAI兼容接口调用API...")
            logger.info("创建chat.completions.create请求...")
            completion = _CLIENT.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            
            logger.info(f"API调用成功，响应类型: {type(completion)}")
            
            # 获取token使用量
            try:
                usage = getattr(completion, "usage", None)
                if usage:
                    logger.info(f"响应usage类型: {type(usage)}")
                    token_usage = {
                        "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                        "completion_tokens": getattr(usage, "completion_tokens", 0),
                        "total_tokens": getattr(usage, "total_tokens", 0)
                    }
                    logger.info(f"Token使用量: {token_usage}")
                else:
                    logger.error(f"响应没有usage属性: {dir(completion)}")
                    token_usage = {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
            except Exception as e:
                logger.error(f"获取token使用量失败: {e}")
                token_usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            
            try:
                content = completion.choices[0].message.content
                logger.info(f"响应内容长度: {len(content)}")
                logger.info(f"响应内容前50个字符: {content[:50]}...")
                return content, token_usage
            except Exception as e:
                logger.error(f"获取响应内容失败: {e}")
                try:
                    content = completion.choices[0].text
                    logger.info(f"使用text属性获取响应内容，长度: {len(content)}")
                    return content, token_usage
                except Exception as e2:
                    logger.error(f"使用text属性获取响应内容也失败: {e2}")
                    content = str(completion)
                    logger.info(f"使用str(completion)获取响应内容，长度: {len(content)}")
                    return content, token_usage
    except Exception as e:
        logger.error(f"API调用失败: {e}")
        logger.error(f"使用的模型: {model}")
        logger.error(f"API提供商: {_CLIENT_PROVIDER}")
        # 打印更详细的错误信息
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        raise


def generate_dialog_script(text: str, style: str = "casual", participants: int = 2, max_tokens: int = 4096, model: str = "deepseek-v3.2") -> Dict[str, Any]:
    logger.info("开始生成对话脚本...")
    logger.info(f"输入文本长度: {len(text)}")
    logger.info(f"风格: {style}")
    logger.info(f"参与人数: {participants}")
    logger.info(f"max_tokens: {max_tokens}")
    logger.info(f"模型: {model}")
    
    # 根据API提供商选择合适的模型名称
    if _CLIENT_PROVIDER == "dashscope" or _CLIENT_PROVIDER == "dashscope_sdk":
        # 千问API支持的模型名称
        logger.info("使用千问API，检查模型名称...")
        if model not in ["qwen-plus", "qwen-turbo", "qwen-max"]:
            # 默认使用qwen-turbo
            logger.info(f"模型 {model} 不是千问API支持的模型，将使用默认模型 qwen-turbo")
            model = "qwen-turbo"
        logger.info(f"最终使用的模型: {model}")
    system_prompt = _get_style_prompt(style, participants)
    logger.info(f"system_prompt生成完成，长度: {len(system_prompt)}")
    
    user_prompt = f"""请基于以下新闻创作一个引人入胜的播客对话：

**新闻标题**：{text[:100]}...

**新闻完整内容**：
{text}

**创作指令（按重要性排序）：**

1. **深度挖掘（必做）**：
   - 不要停留在表面现象，追问"为什么"（至少3个层次）
   - 找出新闻中未被充分讨论的矛盾点和隐性成本
   - 举例说明：如果一个概念在原文中提及，请用更生动的例子重新解释

2. **独特见解（必做）**：
   - 提出至少2个原文没有的见解或视角
   - 将此事与更广泛的社会趋势、人性弱点、经济规律联系起来
   - 给听众带来"原来如此"的顿悟时刻

3. **具体化抽象（必做）**：
   - 选择原文中1-2个具体人物故事，展开想象他们的完整遭遇
   - 用"假如你是..."的方式让听众代入
   - 将数据转化为可感知的经验（如"50万辆僵尸车等于多少个足球场？"）

4. **信息完整性（重要）**：
   - 确保覆盖原文的主要部分：现象、企业困境、政府措施、专家观点、国际对比、技术方案、记者反思
   - 但不要机械罗列，而是有机融入对话中

5. **听众吸引（重要）**：
   - 开头30秒必须有"钩子"（令人惊讶的事实、反问、个人故事）
   - 每3-5轮对话要有一个小高潮或观点冲突
   - 结尾要给听众留下具体的行动思考题

6. **专业与通俗平衡**：
   - 解释专业术语时要用生活化类比（如"电子围栏就像电子狗链"）
   - 保留关键数据，但说明其意义而不仅仅是数字

**对话要求：**
- 必须是真正的对话，主持人提问，嘉宾回答
- 角色要交替发言，不能连续多人发言
- 对话要口语化，像真实播客一样
- 每段对话2-5句，自然停顿
- 体现你的独特理解和感悟
- 加入互动：主持人引导话题，嘉宾发表观点
- 根据风格（{style}）调整语气
- **重要：不要擅自给主持人和嘉宾起名字，只能使用"主持人"、"嘉宾A"、"嘉宾B"等代称**

输出JSON格式：
{{
  "roles": [
    {{"id": "host", "name": "主持人", "title": "资深媒体人"}},
    {{"id": "guest", "name": "嘉宾", "title": "城市治理专家"}}
  ],
  "segments": [
    {{"role": "host", "text": "主持人开场白，用钩子吸引听众"}},
    {{"role": "guest", "text": "嘉宾回应，发表见解"}},
    {{"role": "host", "text": "主持人追问，引导深入"}},
    {{"role": "guest", "text": "嘉宾回答，表达独特见解"}}
  ],
  "notes": "制作备注（可选，说明本段的创作意图）"
}}

直接返回JSON，不要其他文字。确保对话自然流畅，每个角色发言有明显个性区别。"""

    logger.info(f"user_prompt生成完成，长度: {len(user_prompt)}")

    try:
        logger.info("开始调用API生成对话...")
        resp_text, token_usage = _call_qwen_api(user_prompt, system_prompt=system_prompt, model=model, max_tokens=max_tokens)
        logger.info(f"API调用完成，响应文本长度: {len(resp_text)}")
        logger.info(f"Token使用量: {token_usage}")
        
        try:
            logger.info("尝试解析JSON响应...")
            parsed = json.loads(resp_text)
            logger.info("JSON解析成功！")
            logger.info(f"解析后的角色数量: {len(parsed.get('roles', []))}")
            logger.info(f"解析后的对话段数: {len(parsed.get('segments', []))}")
            parsed.setdefault("raw", resp_text)
            parsed.setdefault("token_usage", token_usage)
            parsed.setdefault("model", model)
            logger.info("对话脚本生成成功！")
            return parsed
        except Exception as e:
            logger.warning(f"JSON解析失败: {e}")
            logger.info("尝试使用正则表达式提取JSON...")
            import re
            json_match = re.search(r'\{[\s\S]*\}', resp_text)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    logger.info("正则表达式提取JSON成功！")
                    logger.info(f"解析后的角色数量: {len(parsed.get('roles', []))}")
                    logger.info(f"解析后的对话段数: {len(parsed.get('segments', []))}")
                    parsed.setdefault("raw", resp_text)
                    parsed.setdefault("token_usage", token_usage)
                    parsed.setdefault("model", model)
                    logger.info("对话脚本生成成功！")
                    return parsed
                except Exception as e2:
                    logger.error(f"正则表达式提取JSON也失败: {e2}")
            
            logger.info("返回原始响应文本...")
            return {
                "roles": [{"id": "host", "name": "主持人", "title": "资深媒体人"}, {"id": "guest", "name": "嘉宾", "title": "城市治理专家"}],
                "segments": [{"role": "host", "text": resp_text}],
                "raw": resp_text,
                "token_usage": token_usage,
                "model": model,
                "error": "JSON解析失败"
            }
    except Exception as e:
        # 当模型调用失败时，不再输出机械拆分的文本，而是返回明确的错误信息
        logger.error(f"模型调用失败: {e}")
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        error_msg = f"模型调用失败: {str(e)}"
        return {
            "roles": [{"id": "host", "name": "系统", "title": "错误信息"}],
            "segments": [{"role": "host", "text": "模型调用失败，请检查API配置和网络连接。"}],
            "raw": error_msg,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "error": error_msg,
            "model": model,
            "model_error": True
        }
