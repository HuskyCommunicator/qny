"""
项目常量定义模块
"""
from enum import Enum
from typing import List, Dict, Any


class ResponseCode(Enum):
    """响应状态码枚举"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    VALIDATION_ERROR = 422
    INTERNAL_ERROR = 500


class UserRole(Enum):
    """用户角色枚举"""
    USER = "user"
    ADMIN = "admin"


class ParticipantType(Enum):
    """场景参与者类型枚举"""
    USER = "user"
    AI = "ai"
    OBSERVER = "observer"


class SceneStatus(Enum):
    """场景状态枚举"""
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"


class FeedbackType(Enum):
    """反馈类型枚举"""
    LIKE = "like"
    DISLIKE = "dislike"
    RATING = "rating"


class AlgorithmType(Enum):
    """推荐算法类型枚举"""
    COLLABORATIVE = "collaborative"
    CONTENT = "content"
    POPULAR = "popular"
    HYBRID = "hybrid"


# 系统常量
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_TOKEN_EXPIRE_MINUTES = 60
CACHE_EXPIRE_MINUTES = 30

# 角色分类
ROLE_CATEGORIES = [
    "文学角色",
    "历史人物",
    "教育专家",
    "心理咨询",
    "科技专家",
    "娱乐明星",
    "虚构角色",
    "其他"
]

# 反馈原因模板
FEEDBACK_REASONS = {
    "专业度": ["回答专业", "知识丰富", "逻辑清晰", "解释详细"],
    "相关性": ["回答相关", "切合主题", "理解准确", "针对性强"],
    "实用性": ["实用建议", "解决问题", "可操作性强", "有价值"],
    "语言表达": ["表达清晰", "语言优美", "易于理解", "表达生动"],
    "创新性": ["观点新颖", "思路独特", "有创意", "启发思考"],
    "态度友好": ["态度友善", "耐心细致", "乐于助人", "有同理心"]
}