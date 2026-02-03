import os
import json
from typing import Any, Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_CLIENT = None
_CLIENT_PROVIDER = None

try:
    from openai import OpenAI
    openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
    if openai_key:
        base_url = os.getenv("DASHSCOPE_BASE_URL")
        if base_url:
            _CLIENT = OpenAI(api_key=openai_key, base_url=base_url)
            _CLIENT_PROVIDER = "dashscope"
        else:
            _CLIENT = OpenAI(api_key=openai_key)
            _CLIENT_PROVIDER = "openai"
except Exception:
    _CLIENT = None
    _CLIENT_PROVIDER = None


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


def _call_qwen_api(prompt: str, system_prompt: str = None, model: str = "deepseek-v3.2", max_tokens: int = 4096) -> tuple:
    if _CLIENT is None:
        raise RuntimeError("Qwen/OpenAI client 未配置（请设置 OPENAI_API_KEY 或 DASHSCOPE_API_KEY）")

    if system_prompt is None:
        system_prompt = "你是一个擅长将文章改写为对话式播客脚本的助手。"

    completion = _CLIENT.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    
    # 获取token使用量
    token_usage = {
        "prompt_tokens": getattr(completion, "usage", {}).get("prompt_tokens", 0),
        "completion_tokens": getattr(completion, "usage", {}).get("completion_tokens", 0),
        "total_tokens": getattr(completion, "usage", {}).get("total_tokens", 0)
    }
    
    try:
        content = completion.choices[0].message.content
        return content, token_usage
    except Exception:
        try:
            content = completion.choices[0].text
            return content, token_usage
        except Exception:
            content = str(completion)
            return content, token_usage


def generate_dialog_script(text: str, style: str = "casual", participants: int = 2, max_tokens: int = 4096) -> Dict[str, Any]:
    system_prompt = _get_style_prompt(style, participants)
    
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

    try:
        resp_text, token_usage = _call_qwen_api(user_prompt, system_prompt=system_prompt, max_tokens=max_tokens)
        
        try:
            parsed = json.loads(resp_text)
            parsed.setdefault("raw", resp_text)
            parsed.setdefault("token_usage", token_usage)
            return parsed
        except Exception:
            import re
            json_match = re.search(r'\{[\s\S]*\}', resp_text)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    parsed.setdefault("raw", resp_text)
                    parsed.setdefault("token_usage", token_usage)
                    return parsed
                except Exception:
                    pass
            
            return {
                "roles": [{"id": "host", "name": "主持人", "title": "资深媒体人"}, {"id": "guest", "name": "嘉宾", "title": "城市治理专家"}],
                "segments": [{"role": "host", "text": resp_text}],
                "raw": resp_text,
                "token_usage": token_usage,
                "error": "JSON解析失败"
            }
    except Exception as e:
        import re
        sentences = [s.strip() for s in re.split(r'(?<=[。！？.!?])\s*', text) if s.strip()]
        roles = []
        for i in range(participants):
            if i == 0:
                roles.append({"id": f"r{i+1}", "name": "主持人", "title": "资深媒体人"})
            else:
                roles.append({"id": f"r{i+1}", "name": f"嘉宾{i}", "title": "城市治理专家"})

        segments = []
        for idx, s in enumerate(sentences):
            segments.append({"role": roles[idx % participants]["id"], "text": s})

        raw = "\n".join(sentences[:5])
        return {
            "roles": roles,
            "segments": segments,
            "raw": raw,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "error": str(e)
        }
