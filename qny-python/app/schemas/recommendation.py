"""
推荐系统相关的数据验证schema
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from .role import RoleOut


class RecommendationItem(BaseModel):
    """推荐项"""
    role: RoleOut
    score: float = Field(..., description="推荐分数", ge=0.0, le=1.0)
    reason: str = Field(..., description="推荐原因")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    recommendations: List[RecommendationItem]
    total_count: int = Field(..., description="推荐总数")
    algorithm_used: str = Field(..., description="使用的推荐算法")
    user_profile_summary: Optional[Dict[str, Any]] = Field(None, description="用户画像摘要")


class UserBehaviorProfile(BaseModel):
    """用户行为画像"""
    user_id: int
    total_sessions: int = Field(..., description="总会话数")
    total_messages: int = Field(..., description="总消息数")
    activity_level: int = Field(..., description="活跃天数")
    favorite_categories: List[tuple] = Field(..., description="喜爱的分类")
    favorite_tags: List[tuple] = Field(..., description="喜爱的标签")
    most_used_roles: List[tuple] = Field(..., description="最常用的角色")


class RecommendationExplanation(BaseModel):
    """推荐解释"""
    role_name: str
    reasons: List[str]


class RecommendationAnalytics(BaseModel):
    """推荐分析数据"""
    total_recommendations: int = Field(..., description="总推荐次数")
    click_through_rate: float = Field(..., description="点击率", ge=0.0, le=1.0)
    popular_roles: List[Dict[str, Any]] = Field(..., description="热门角色统计")
    user_satisfaction: float = Field(..., description="用户满意度", ge=0.0, le=1.0)


class RecommendationFeedback(BaseModel):
    """推荐反馈"""
    recommendation_id: Optional[int] = Field(None, description="推荐ID")
    role_id: int = Field(..., description="角色ID")
    rating: int = Field(..., description="评分", ge=1, le=5)
    feedback: Optional[str] = Field(None, description="反馈内容")
    is_helpful: bool = Field(..., description="是否有帮助")