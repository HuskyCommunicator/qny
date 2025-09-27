from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float, Enum
from datetime import datetime
import enum

from ..core.db import Base

class SceneType(str, enum.Enum):
    """场景类型枚举"""
    DISCUSSION = "discussion"      # 讨论场景
    TEACHING = "teaching"        # 教学场景
    DEBATE = "debate"           # 辩论场景
    COLLABORATION = "collaboration"  # 协作场景
    ENTERTAINMENT = "entertainment"   # 娱乐场景

class SceneStatus(str, enum.Enum):
    """场景状态枚举"""
    ACTIVE = "active"           # 活跃状态
    PAUSED = "paused"          # 暂停状态
    ENDED = "ended"           # 结束状态
    ARCHIVED = "archived"     # 归档状态

class SceneTemplate(Base):
    """场景模板表"""
    __tablename__ = "scene_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, comment="模板名称")
    title = Column(String(200), nullable=False, comment="场景标题")
    description = Column(Text, comment="场景描述")
    scene_type = Column(Enum(SceneType), nullable=False, comment="场景类型")
    max_roles = Column(Integer, default=3, comment="最大角色数量")
    min_roles = Column(Integer, default=2, comment="最小角色数量")
    config = Column(JSON, comment="场景配置")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

class SceneSession(Base):
    """多角色对话场景会话表"""
    __tablename__ = "scene_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, nullable=False, comment="会话ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    template_id = Column(Integer, ForeignKey("scene_templates.id"), nullable=False, comment="模板ID")
    name = Column(String(200), nullable=False, comment="会话名称")
    description = Column(Text, comment="会话描述")
    status = Column(Enum(SceneStatus), default=SceneStatus.ACTIVE, comment="会话状态")
    current_speaker = Column(Integer, ForeignKey("roles.id"), comment="当前发言角色")
    config = Column(JSON, comment="会话配置")
    message_count = Column(Integer, default=0, comment="消息数量")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    ended_at = Column(DateTime, comment="结束时间")

class SceneParticipant(Base):
    """场景参与者表"""
    __tablename__ = "scene_participants"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("scene_sessions.id"), nullable=False, comment="会话ID")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")
    participant_type = Column(String(50), default="ai", comment="参与者类型 (ai/user)")
    join_order = Column(Integer, default=1, comment="加入顺序")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    personality_config = Column(JSON, comment="个性化配置")
    speak_count = Column(Integer, default=0, comment="发言次数")
    last_speak_at = Column(DateTime, comment="最后发言时间")
    created_at = Column(DateTime, default=datetime.utcnow, comment="加入时间")

class SceneMessage(Base):
    """场景消息表"""
    __tablename__ = "scene_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("scene_sessions.id"), nullable=False, comment="会话ID")
    participant_id = Column(Integer, ForeignKey("scene_participants.id"), comment="参与者ID")
    role_id = Column(Integer, ForeignKey("roles.id"), comment="角色ID")
    message_type = Column(String(50), default="text", comment="消息类型 (text/system/action)")
    content = Column(Text, nullable=False, comment="消息内容")
    target_participant_id = Column(Integer, ForeignKey("scene_participants.id"), comment="目标参与者ID")
    context = Column(JSON, comment="上下文信息")
    message_order = Column(Integer, comment="消息序号")
    created_at = Column(DateTime, default=datetime.utcnow, comment="发送时间")

class SceneInteractionRule(Base):
    """场景互动规则表"""
    __tablename__ = "scene_interaction_rules"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("scene_templates.id"), nullable=False, comment="模板ID")
    name = Column(String(100), nullable=False, comment="规则名称")
    rule_type = Column(String(50), nullable=False, comment="规则类型")
    condition = Column(JSON, comment="触发条件")
    action = Column(JSON, comment="执行动作")
    priority = Column(Integer, default=1, comment="优先级")
    is_active = Column(Boolean, default=True, comment="是否启用")
    description = Column(Text, comment="规则描述")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

class SceneRecommendation(Base):
    """场景推荐表"""
    __tablename__ = "scene_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    template_id = Column(Integer, ForeignKey("scene_templates.id"), nullable=False, comment="模板ID")
    score = Column(Float, default=0.0, comment="推荐分数")
    reason = Column(Text, comment="推荐原因")
    is_clicked = Column(Boolean, default=False, comment="是否点击")
    is_used = Column(Boolean, default=False, comment="是否使用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="推荐时间")