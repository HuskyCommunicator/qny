from typing import List, Dict, Optional, Generator
import random
import os
import time
import requests
import json
from sqlalchemy.orm import Session
from openai import OpenAI
from ..core.config import settings
from ..core.db import get_db
from ..models.role import Role


# 角色化假回复模板
ROLE_MOCK_RESPONSES = {
    "哈利波特": [
        "魔法的世界真是奇妙！你的问题让我想起了霍格沃茨的学习时光。",
        "我记得邓布利多校长说过类似的话， wisdom comes from experience。",
        "这让我想起了罗恩和赫敏的观点，我们应该一起分析这个问题。",
        "在霍格沃茨，我们学会了面对困难时要勇敢。",
        "魔法不仅仅是咒语，更重要的是智慧和理解。"
    ],
    "苏格拉底": [
        "请告诉我，你为什么会这么认为？让我们通过提问来寻找真理。",
        "你的假设是什么？让我们一步步分析，不要急于下结论。",
        "认识自己的无知是智慧的开始。你能解释更多吗？",
        "让我们通过对话来探索这个问题，真理越辩越明。",
        "你说得很有趣，但你能给出证据来支持你的观点吗？"
    ],
    "夏洛克·福尔摩斯": [
        "亲爱的朋友，这个案件很有趣。让我们从细节开始分析。",
        " Elementary！答案往往隐藏在最明显的细节中。",
        "我观察到了几个关键线索，让我为你推理一下。",
        "排除所有不可能因素，剩下的无论多么难以置信，都是真相。",
        "数据！数据！数据！没有粘土我无法制造砖块。"
    ],
    "爱因斯坦": [
        "想象力比知识更重要。让我们从另一个角度思考这个问题。",
        "一切都应该尽可能简单，但不能过于简单。你的观点很有趣。",
        "在危机中，想象力比知识更重要。让我们继续探索。",
        "科学没有边界，人类的探索精神也是如此。",
        "生活的关键在于保持好奇心，就像孩子一样。"
    ],
    "心理咨询师": [
        "我理解你的感受，让我们一起来探讨这个问题。",
        "每个人都有自己的故事，你愿意分享更多吗？",
        "倾听是治疗的第一步。我在这里陪伴你。",
        "你的情绪是正常的，让我们一起找到解决办法。",
        "自我关怀很重要。你今天对自己好吗？"
    ],
    "编程助手": [
        "编程是一门艺术，需要逻辑和创造力的完美结合。",
        "让我帮你分析这个问题，我们可以从基础开始逐步构建解决方案。",
        "代码是最好的文档，清晰的代码本身就是很好的说明。",
        "记住，每个程序员都会遇到bug，这是学习过程的一部分。",
        "我建议先理解问题的本质，然后再考虑具体的实现方式。"
    ],
    "Python编程助手": [
        "Python是一门优雅的编程语言，让我们从基础开始学习。",
        "我建议先掌握Python的基本语法，然后再深入到高级特性。",
        "Python的哲学是'简单胜过复杂'，让我们保持代码的简洁。",
        "你可以通过实际项目来学习Python，这是最有效的方式。",
        "记住，Python有丰富的文档和社区支持，遇到问题时不要犹豫去查询。"
    ],
    "前端开发顾问": [
        "前端开发需要兼顾美观和功能性，让我们找到最佳平衡点。",
        "我建议先了解用户需求，然后选择合适的技术栈。",
        "响应式设计很重要，确保你的应用在各种设备上都能良好运行。",
        "性能优化是前端开发的关键，要注意代码分割和懒加载。",
        "用户体验是最重要的，每个设计决策都应该以用户为中心。"
    ]
}

# 默认回复（当角色不存在时使用）
DEFAULT_RESPONSES = [
    "我理解你的问题，让我认真思考一下。",
    "这是一个很好的问题，我的看法是...",
    "谢谢你的分享，我觉得很有意思。",
    "让我们继续这个话题，我很感兴趣。",
    "你的观点很独特，我想了解更多。"
]


def generate_reply(messages: List[Dict[str, str]], role_id: Optional[int] = None, db: Session = None) -> str:
    """
    生成角色化回复（使用假回复模拟AI）

    Args:
        messages: 聊天历史记录
        role_id: 角色ID，用于获取角色化回复
        db: 数据库会话，用于获取角色信息

    Returns:
        str: AI回复内容
    """
    if not messages:
        return "你好！我是AI助手，很高兴与你对话。"

    # 获取用户最后一条消息
    last_message = messages[-1]
    user_content = last_message.get('content', '')

    # 如果有角色ID，尝试获取角色化回复
    if role_id and db:
        try:
            # 查询角色信息
            role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
            if role:
                # 根据角色名称选择回复模板
                role_responses = ROLE_MOCK_RESPONSES.get(role.name, DEFAULT_RESPONSES)
                return random.choice(role_responses)
        except Exception:
            # 如果查询失败，使用默认回复
            pass

    # 没有角色或查询失败时，使用默认回复
    return random.choice(DEFAULT_RESPONSES)


def generate_reply_with_context(messages: List[Dict[str, str]], role_name: str = None) -> str:
    """
    根据角色名称生成回复（简化版本）

    Args:
        messages: 聊天历史记录
        role_name: 角色名称

    Returns:
        str: AI回复内容
    """
    if not messages:
        return "你好！我是AI助手，很高兴与你对话。"

    # 根据角色名称选择回复模板
    if role_name and role_name in ROLE_MOCK_RESPONSES:
        responses = ROLE_MOCK_RESPONSES[role_name]
    else:
        responses = DEFAULT_RESPONSES

    return random.choice(responses)


def generate_reply_real_llm(messages: List[Dict[str, str]], role_id: Optional[int] = None, db: Session = None) -> str:
    """
    使用真实LLM API生成回复

    Args:
        messages: 聊天历史记录
        role_id: 角色ID，用于获取角色化提示
        db: 数据库会话，用于获取角色信息

    Returns:
        str: AI回复内容
    """
    # 检查是否配置了真实API
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY')
    api_url = os.getenv('LLM_API_URL', 'https://api.openai.com/v1/chat/completions')

    if not api_key:
        # 如果没有配置API密钥，回退到模拟回复
        return generate_reply_mock(messages, role_id, db)

    try:
        # 构建消息列表
        api_messages = []

        # 添加角色系统提示
        if role_id and db:
            try:
                role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
                if role and role.system_prompt:
                    # 添加角色系统提示
                    api_messages.append({
                        "role": "system",
                        "content": role.system_prompt
                    })
            except Exception:
                pass

        # 添加对话历史
        for msg in messages[-10:]:  # 只使用最近10条消息，避免token过多
            role = "user" if msg.get('role') == 'user' else "assistant"
            api_messages.append({
                "role": role,
                "content": msg.get('content', '')
            })

        # 如果没有系统提示，添加默认系统提示
        if not any(msg['role'] == 'system' for msg in api_messages):
            api_messages.insert(0, {
                "role": "system",
                "content": "你是一个智能助手，请根据用户的提问提供有帮助的回答。"
            })

        # 调用LLM API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": os.getenv('LLM_MODEL', 'gpt-3.5-turbo'),
            "messages": api_messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    except Exception as e:
        # 如果API调用失败，回退到模拟回复
        print(f"LLM API调用失败: {e}")
        return generate_reply_mock(messages, role_id, db)


def generate_reply_mock(messages: List[Dict[str, str]], role_id: Optional[int] = None, db: Session = None) -> str:
    """
    生成角色化回复（使用假回复模拟AI）

    Args:
        messages: 聊天历史记录
        role_id: 角色ID，用于获取角色化回复
        db: 数据库会话，用于获取角色信息

    Returns:
        str: AI回复内容
    """
    if not messages:
        return "你好！我是AI助手，很高兴与你对话。"

    # 获取用户最后一条消息
    last_message = messages[-1]
    user_content = last_message.get('content', '')

    # 如果有角色ID，尝试获取角色化回复
    if role_id and db:
        try:
            # 查询角色信息
            role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
            if role:
                # 根据角色名称选择回复模板
                role_responses = ROLE_MOCK_RESPONSES.get(role.name, DEFAULT_RESPONSES)
                return random.choice(role_responses)
        except Exception:
            # 如果查询失败，使用默认回复
            pass

    # 没有角色或查询失败时，使用默认回复
    return random.choice(DEFAULT_RESPONSES)


# 主要接口函数，根据配置决定使用真实API还是模拟
def generate_reply(messages: List[Dict[str, str]], role_id: Optional[int] = None, db: Session = None) -> str:
    """
    生成AI回复（支持真实LLM API和模拟回复）

    Args:
        messages: 聊天历史记录
        role_id: 角色ID，用于获取角色化回复
        db: 数据库会话，用于获取角色信息

    Returns:
        str: AI回复内容
    """
    # 检查是否启用真实LLM
    use_real_llm = os.getenv('USE_REAL_LLM', 'false').lower() == 'true'

    if use_real_llm:
        return generate_reply_real_llm(messages, role_id, db)
    else:
        return generate_reply_mock(messages, role_id, db)


