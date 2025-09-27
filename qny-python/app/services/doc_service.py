from typing import List

import io
import re

from PyPDF2 import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(texts)


def extract_text_from_markdown(file_bytes: bytes) -> str:
    # 简化：直接当作 utf-8 文本处理，剔除部分 markdown 标记
    text = file_bytes.decode("utf-8", errors="ignore")
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"^#+ ", " ", text, flags=re.M)
    return text


def chunk_text(text: str, max_len: int = 600) -> List[str]:
    # 简单按句子切分，再合并到接近 max_len
    sentences = re.split(r"(?<=[。！？.!?])\s+", text)
    chunks: List[str] = []
    buf = []
    cur = 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if cur + len(s) > max_len and buf:
            chunks.append("".join(buf))
            buf = [s]
            cur = len(s)
        else:
            buf.append(s)
            cur += len(s)
    if buf:
        chunks.append("".join(buf))
    return chunks


