from typing import List, Dict, Optional
import os
import time
from openai import OpenAI

from ..core.config import settings


def _get_qwen_client() -> OpenAI:
    api_key = settings.dashscope_api_key or os.getenv("DASHSCOPE_API_KEY")
    base_url = settings.llm_base_url
    return OpenAI(api_key=api_key, base_url=base_url, timeout=settings.llm_timeout_sec)


def _with_retry(fn, max_retries: int, base_delay: float = 0.5):
    attempt = 0
    while True:
        try:
            return fn()
        except Exception as e:
            attempt += 1
            if attempt > max_retries:
                raise e
            time.sleep(base_delay * (2 ** (attempt - 1)))


def _build_messages(role: str, user_message: str, history: Optional[List[Dict[str, str]]], retrieved_docs: Optional[List[str]], full_prompt: Optional[str], messages: List[Dict[str, str]]):
    msgs: List[Dict[str, str]] = []
    if full_prompt:
        msgs.append({"role": "system", "content": full_prompt})
    # 把已有的 history messages 直接拼上（兼容之前逻辑）
    msgs.extend(messages)
    # 再确保最后的用户消息存在
    if not messages or messages[-1].get("role") != "user":
        msgs.append({"role": "user", "content": user_message})
    return msgs


def generate_reply(messages: List[Dict[str, str]], full_prompt: Optional[str] = None, role: Optional[str] = None, user_message: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None, retrieved_docs: Optional[List[str]] = None) -> str:
    """调用通义千问真实模型产生回复，并包含超时/重试。
    full_prompt 为空时也可直接使用 messages。
    """
    # 如未配置或本地调试，fallback 到占位
    if not settings.dashscope_api_key:
        if full_prompt:
            return f"[PROMPT_OK] {messages[-1].get('content', '') if messages else ''}"
        return f"Echo: {messages[-1].get('content', '') if messages else ''}"

    client = _get_qwen_client()
    msgs = _build_messages(role or "assistant", user_message or (messages[-1].get("content") if messages else ""), history, retrieved_docs, full_prompt, messages)

    def _call():
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=msgs,
        )
        # 新版 SDK 返回对象结构可能为 .choices[0].message.content
        choice = resp.choices[0]
        # 兼容 dict 访问
        content = getattr(choice.message, "content", None)
        if content is None and isinstance(choice, dict):
            content = choice.get("message", {}).get("content")
        return content or ""

    try:
        return _with_retry(_call, settings.llm_max_retries)
    except Exception as e:
        # 回退占位
        return f"[ERROR] {messages[-1].get('content', '') if messages else ''}"


