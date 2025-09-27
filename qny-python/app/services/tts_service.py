def synthesize_speech(text: str) -> bytes:
    """最小占位：返回文本的二进制占位数据。"""
    return f"AUDIO({text})".encode("utf-8")


