from typing import List, Dict


def generate_reply(messages: List[Dict[str, str]]) -> str:
    """最小占位：将最后一句内容回显为助手回复。"""
    if not messages:
        return ""
    last = messages[-1]
    return f"Echo: {last.get('content', '')}"


