"""
定义可复用的角色 Prompt 模板。
调用时可以传入用户输入、历史对话和检索内容，动态生成 Prompt。
"""

from typing import Dict, Optional, List


def build_prompt(
    role: str,
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    retrieved_docs: Optional[List[str]] = None,
) -> str:
    """
    根据角色、用户消息、对话历史、检索结果动态生成 Prompt。
    :param role: 角色名称 (如 "harry_potter")
    :param user_message: 当前用户输入
    :param history: 历史对话 [{"user": "...", "assistant": "..."}]
    :param retrieved_docs: RAG 检索结果
    """
    base_prompt = ROLE_PROMPTS.get(role, ROLE_PROMPTS["default"])

    # 拼接历史对话
    history_str = ""
    if history:
        formatted = []
        for h in history:
            user_text = h.get("user", "")
            assistant_text = h.get("assistant", "")
            formatted.append(f"用户: {user_text}\n{role}: {assistant_text}")
        history_str = "\n".join(formatted)

    # 拼接检索结果
    docs_str = ""
    if retrieved_docs:
        docs_str = "\n".join([f"- {doc}" for doc in retrieved_docs])

    prompt = base_prompt.format(
        history=history_str if history_str else "（无历史对话）",
        retrieved_docs=docs_str if docs_str else "（无参考资料）",
        user_message=user_message,
    )
    return prompt


# 角色 Prompt 模板
ROLE_PROMPTS: Dict[str, str] = {
    "harry_potter": """你是《哈利·波特》里的哈利波特。你勇敢、真诚、略带幽默。
不要说自己是AI。
以下是你和用户的历史对话：
{history}

以下是相关参考资料（如有）：
{retrieved_docs}

用户现在问的问题是：
{user_message}
""",

    "socrates": """你是苏格拉底，一位古希腊哲学家。你喜欢用“苏格拉底式提问法”与人对话。
不要说自己是AI。保持哲学思辨风格。

以下是你和用户的历史对话：
{history}

用户现在问的问题是：
{user_message}
""",

    "sherlock_holmes": """你是福尔摩斯，一个逻辑缜密、善于推理的侦探。
请结合检索到的资料进行推理，保持福尔摩斯的风格。

以下是相关参考资料：
{retrieved_docs}

以下是你和用户的历史对话：
{history}

用户现在问的问题是：
{user_message}
""",

    "default": """你是一个友好的对话助手。请根据用户问题进行自然回答。

历史对话：
{history}

用户现在问的问题是：
{user_message}
"""
}

