"""
成长系统相关的数据验证schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SkillProgress(BaseModel):
    """技能进度信息"""
    skill_name: str = Field(..., description="技能名称")
    skill_description: Optional[str] = Field(None, description="技能描述")
    proficiency_level: int = Field(..., ge=0, le=100, description="熟练度（0-100）")
    is_unlocked: bool = Field(..., description="是否已解锁")
    unlock_level: int = Field(..., description="解锁所需等级")
    usage_count: int = Field(..., ge=0, description="使用次数")


class LevelInfo(BaseModel):
    """等级信息"""
    current_level: int = Field(..., ge=1, description="当前等级")
    current_exp: int = Field(..., ge=0, description="当前经验值")
    next_level_exp: int = Field(..., ge=0, description="下一级所需经验值")
    exp_progress: int = Field(..., ge=0, description="当前等级进度经验值")
    exp_needed: int = Field(..., ge=0, description="升级所需经验值")
    progress_percentage: float = Field(..., ge=0, le=100, description="升级进度百分比")


class FeedbackAnalysis(BaseModel):
    """反馈分析结果"""
    total_feedbacks: int = Field(..., ge=0, description="总反馈数量")
    satisfaction_rate: float = Field(..., ge=0, le=100, description="满意度百分比")
    feedback_distribution: Dict[str, int] = Field(..., description="反馈类型分布")
    common_reasons: List[str] = Field(..., description="常见反馈原因")
    trend_analysis: str = Field(..., description="趋势分析")


class GrowthHistory(BaseModel):
    """成长历史记录"""
    timestamp: datetime = Field(..., description="时间戳")
    event_type: str = Field(..., description="事件类型")
    description: str = Field(..., description="事件描述")
    metadata: Dict[str, Any] = Field(..., description="元数据")


class RoleGrowthSummary(BaseModel):
    """角色成长摘要"""
    role_id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    level: int = Field(..., ge=1, description="角色等级")
    experience: int = Field(..., ge=0, description="总经验值")
    next_level_exp: int = Field(..., ge=0, description="下一级所需经验值")
    exp_progress: int = Field(..., ge=0, description="当前等级进度")
    exp_needed: int = Field(..., ge=0, description="升级所需经验值")
    progress_percentage: float = Field(..., ge=0, le=100, description="升级进度百分比")
    total_conversations: int = Field(..., ge=0, description="总对话次数")
    positive_feedback: int = Field(..., ge=0, description="好评数量")
    negative_feedback: int = Field(..., ge=0, description="差评数量")
    skills: List[SkillProgress] = Field(..., description="技能进度列表")
    satisfaction_rate: float = Field(..., ge=0, le=100, description="满意度")
    growth_rate: float = Field(..., ge=0, description="成长率")


# === 请求参数schemas ===

class FeedbackCreate(BaseModel):
    """创建反馈请求"""
    role_id: int = Field(..., description="角色ID")
    message_id: Optional[int] = Field(None, description="消息ID")
    feedback_type: str = Field(..., description="反馈类型：like/dislike/rating")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分（1-5星）")
    feedback_reason: Optional[str] = Field(None, description="反馈原因")
    comment: Optional[str] = Field(None, description="详细评论")


class FeedbackReason(BaseModel):
    """反馈原因选项"""
    reason: str = Field(..., description="原因文本")
    category: str = Field(..., description="原因分类")


# === 响应schemas ===

class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int = Field(..., description="反馈ID")
    user_id: int = Field(..., description="用户ID")
    role_id: int = Field(..., description="角色ID")
    message_id: Optional[int] = Field(None, description="消息ID")
    feedback_type: str = Field(..., description="反馈类型")
    rating: Optional[int] = Field(None, description="评分")
    feedback_reason: Optional[str] = Field(None, description="反馈原因")
    comment: Optional[str] = Field(None, description="评论")
    created_at: datetime = Field(..., description="创建时间")


class SkillUpdateResponse(BaseModel):
    """技能更新响应"""
    skill_name: str = Field(..., description="技能名称")
    old_proficiency: int = Field(..., description="旧熟练度")
    new_proficiency: int = Field(..., description="新熟练度")
    usage_count: int = Field(..., description="使用次数")
    exp_gained: int = Field(..., description="获得经验值")


class GrowthStats(BaseModel):
    """成长统计数据"""
    role_id: int = Field(..., description="角色ID")
    total_conversations: int = Field(..., description="总对话次数")
    total_feedbacks: int = Field(..., description="总反馈数")
    satisfaction_rate: float = Field(..., description="满意度")
    growth_rate: float = Field(..., description="成长率")
    level_progress: LevelInfo = Field(..., description="等级进度")
    top_skills: List[SkillProgress] = Field(..., description="顶级技能")
    recent_activities: List[GrowthHistory] = Field(..., description="最近活动")


class UserFeedbackStats(BaseModel):
    """用户反馈统计"""
    total_given: int = Field(..., description="给出的反馈总数")
    satisfaction_rate: float = Field(..., description="个人满意度")
    favorite_roles: List[Dict[str, Any]] = Field(..., description="最喜欢的角色")
    feedback_trend: str = Field(..., description="反馈趋势")


class RoleSkillResponse(BaseModel):
    """角色技能响应"""
    id: int = Field(..., description="技能ID")
    role_id: int = Field(..., description="角色ID")
    skill_name: str = Field(..., description="技能名称")
    skill_description: Optional[str] = Field(None, description="技能描述")
    skill_category: Optional[str] = Field(None, description="技能分类")
    proficiency_level: int = Field(..., ge=0, le=100, description="熟练度")
    is_unlocked: bool = Field(..., description="是否已解锁")
    unlock_level: int = Field(..., description="解锁等级")
    usage_count: int = Field(..., ge=0, description="使用次数")
    skill_metadata: Optional[Dict[str, Any]] = Field(None, description="技能元数据")
    created_at: datetime = Field(..., description="创建时间")


class GrowthLeaderboard(BaseModel):
    """成长排行榜"""
    role_id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    level: int = Field(..., description="等级")
    experience: int = Field(..., description="经验值")
    total_conversations: int = Field(..., description="总对话数")
    satisfaction_rate: float = Field(..., description="满意度")
    rank: int = Field(..., description="排名")


class FeedbackReasonOptions(BaseModel):
    """反馈原因选项"""
    like_reasons: List[FeedbackReason] = Field(..., description="点赞原因")
    dislike_reasons: List[FeedbackReason] = Field(..., description="点踩原因")
    rating_reasons: List[FeedbackReason] = Field(..., description="评分原因")