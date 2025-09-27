"""
通用工具函数模块
"""
import re
import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional, Union, TypeVar, Callable
from datetime import datetime, timedelta
from functools import wraps
from pydantic import BaseModel
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core.exceptions import ValidationError


T = TypeVar('T')


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())


def generate_hash(text: str, algorithm: str = 'md5') -> str:
    """生成哈希值"""
    if algorithm == 'md5':
        return hashlib.md5(text.encode()).hexdigest()
    elif algorithm == 'sha256':
        return hashlib.sha256(text.encode()).hexdigest()
    else:
        raise ValueError(f"不支持的哈希算法: {algorithm}")


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> Dict[str, Any]:
    """验证密码强度"""
    result = {
        "is_valid": True,
        "errors": []
    }

    if len(password) < 6:
        result["is_valid"] = False
        result["errors"].append("密码长度不能少于6位")

    if len(password) > 128:
        result["is_valid"] = False
        result["errors"].append("密码长度不能超过128位")

    if not re.search(r'[A-Z]', password):
        result["errors"].append("密码应包含至少一个大写字母")

    if not re.search(r'[a-z]', password):
        result["errors"].append("密码应包含至少一个小写字母")

    if not re.search(r'\d', password):
        result["errors"].append("密码应包含至少一个数字")

    return result


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """清理输入文本"""
    if not text:
        return ""

    # 移除危险字符
    text = re.sub(r'[<>"\']', '', text)

    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]

    return text.strip()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """解析日期时间字符串"""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def calculate_age(birth_date: datetime) -> int:
    """计算年龄"""
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, indent: int = None) -> str:
    """安全的JSON序列化"""
    try:
        return json.dumps(obj, indent=indent, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return "{}"


def validate_pagination_params(page: int, page_size: int) -> tuple[int, int]:
    """验证分页参数"""
    if page < 1:
        page = 1

    if page_size < 1:
        page_size = DEFAULT_PAGE_SIZE
    elif page_size > MAX_PAGE_SIZE:
        page_size = MAX_PAGE_SIZE

    return page, page_size


def paginate_list(items: List[T], page: int, page_size: int) -> tuple[List[T], Dict[str, Any]]:
    """分页处理列表"""
    total = len(items)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    paginated_items = items[start_idx:end_idx]

    pagination_info = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0
    }

    return paginated_items, pagination_info


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    import time
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个字典"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """扁平化字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def is_valid_url(url: str) -> bool:
    """验证URL格式"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def extract_text_from_html(html: str) -> str:
    """从HTML中提取纯文本"""
    # 简单的HTML标签移除
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)


def validate_phone_number(phone: str) -> bool:
    """验证手机号格式（中国大陆）"""
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None


def calculate_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度（简单版本）"""
    if not text1 and not text2:
        return 1.0
    if not text1 or not text2:
        return 0.0

    # 使用编辑距离计算相似度
    from difflib import SequenceMatcher
    return SequenceMatcher(None, text1, text2).ratio()


def get_time_ago(dt: datetime) -> str:
    """获取时间差描述"""
    now = datetime.now()
    diff = now - dt

    if diff.days > 365:
        return f"{diff.days // 365}年前"
    elif diff.days > 30:
        return f"{diff.days // 30}个月前"
    elif diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}小时前"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}分钟前"
    else:
        return "刚刚"


class PydanticUtils:
    """Pydantic相关工具"""

    @staticmethod
    def model_to_dict(model: BaseModel, exclude_none: bool = True) -> Dict[str, Any]:
        """Pydantic模型转字典"""
        return model.model_dump(exclude_none=exclude_none)

    @staticmethod
    def dict_to_model(data: Dict[str, Any], model_class: type[BaseModel]) -> BaseModel:
        """字典转Pydantic模型"""
        try:
            return model_class(**data)
        except Exception as e:
            raise ValidationError(f"数据转换失败: {str(e)}")

    @staticmethod
    def validate_data(data: Dict[str, Any], model_class: type[BaseModel]) -> BaseModel:
        """验证数据"""
        try:
            return model_class.model_validate(data)
        except Exception as e:
            raise ValidationError(f"数据验证失败: {str(e)}")