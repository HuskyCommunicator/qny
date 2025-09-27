from typing import List, Dict, Optional, Generator
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
        # 使用完整的 prompt（已包含历史对话）
        msgs.append({"role": "system", "content": full_prompt})
        # 只添加当前用户消息
        msgs.append({"role": "user", "content": user_message})
    else:
        # 如果没有 full_prompt，使用 messages 数组
        msgs.extend(messages)
        # 确保最后的用户消息存在
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


def generate_reply_stream(messages: List[Dict[str, str]], full_prompt: Optional[str] = None, role: Optional[str] = None, user_message: Optional[str] = None, history: Optional[List[Dict[str, str]]] = None, retrieved_docs: Optional[List[str]] = None) -> Generator[str, None, None]:
    """流式调用通义千问模型产生回复"""
    # 如未配置或本地调试，fallback 到占位
    if not settings.dashscope_api_key:
        if full_prompt:
            yield f"[PROMPT_OK] {messages[-1].get('content', '') if messages else ''}"
        else:
            yield f"Echo: {messages[-1].get('content', '') if messages else ''}"
        return

    client = _get_qwen_client()
    msgs = _build_messages(role or "assistant", user_message or (messages[-1].get("content") if messages else ""), history, retrieved_docs, full_prompt, messages)

    def _call_stream():
        stream = client.chat.completions.create(
            model=settings.llm_model,
            messages=msgs,
            stream=True,  # 启用流式输出
        )
        return stream

    try:
        stream = _with_retry(_call_stream, settings.llm_max_retries)
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
                
    except Exception as e:
        # 回退占位
        yield f"[ERROR] {messages[-1].get('content', '') if messages else ''}"


