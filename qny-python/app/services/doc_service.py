from typing import List
import json

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


def extract_text_from_json(file_bytes: bytes) -> str:
    """
    从JSON文件中提取文本内容
    
    Args:
        file_bytes: JSON文件的二进制数据
    
    Returns:
        str: 提取的文本内容
    """
    try:
        # 解码JSON文件
        json_text = file_bytes.decode("utf-8", errors="ignore")
        data = json.loads(json_text)
        
        # 递归提取文本内容
        def extract_text_recursive(obj, path=""):
            texts = []
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    texts.extend(extract_text_recursive(value, current_path))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    texts.extend(extract_text_recursive(item, current_path))
            elif isinstance(obj, str):
                # 字符串值，包含路径信息
                if obj.strip():
                    texts.append(f"{path}: {obj}")
            elif isinstance(obj, (int, float)):
                # 数值，包含路径信息
                texts.append(f"{path}: {obj}")
            elif isinstance(obj, bool):
                # 布尔值，包含路径信息
                texts.append(f"{path}: {obj}")
            elif obj is None:
                # null值，包含路径信息
                texts.append(f"{path}: null")
            
            return texts
        
        # 提取所有文本内容
        extracted_texts = extract_text_recursive(data)
        
        # 合并文本，添加换行
        result = "\n".join(extracted_texts)
        
        # 如果提取的文本为空，返回原始JSON字符串
        if not result.strip():
            return json_text
        
        return result
        
    except json.JSONDecodeError:
        # JSON解析失败，返回原始文本
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception:
        # 其他错误，返回原始文本
        return file_bytes.decode("utf-8", errors="ignore")


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


