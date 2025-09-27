from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from ..core.db import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="角色名称")
    description = Column(Text, nullable=True, comment="角色描述")
    system_prompt = Column(Text, nullable=False, comment="角色系统提示词")
    avatar_url = Column(String(500), nullable=True, comment="角色头像URL")
    is_public = Column(Boolean, default=True, comment="是否为公开角色")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建者ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # 角色配置
    config = Column(JSON, nullable=True, comment="角色配置参数")

    # 标签和分类
    tags = Column(JSON, nullable=True, comment="角色标签")
    category = Column(String(50), nullable=True, comment="角色分类")

    # 成长系统字段
    level = Column(Integer, default=1, comment="角色等级")
    experience = Column(Integer, default=0, comment="经验值")
    total_conversations = Column(Integer, default=0, comment="总对话次数")
    positive_feedback = Column(Integer, default=0, comment="好评数量")
    negative_feedback = Column(Integer, default=0, comment="差评数量")
    growth_stats = Column(JSON, nullable=True, comment="成长统计数据")

    # 关联关系
    creator = relationship("User", back_populates="created_roles")
    user_roles = relationship("UserRole", back_populates="role")
    chat_messages = relationship("ChatMessage", back_populates="role")
    chat_sessions = relationship("ChatSession", back_populates="role")

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")
    is_favorite = Column(Boolean, default=False, comment="是否收藏")
    custom_name = Column(String(100), nullable=True, comment="用户自定义角色名称")
    custom_config = Column(JSON, nullable=True, comment="用户自定义配置")
    usage_count = Column(Integer, default=0, comment="使用次数")
    last_used_at = Column(DateTime(timezone=True), nullable=True, comment="最后使用时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关联关系
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=True, comment="消息ID")
    feedback_type = Column(String(20), nullable=False, comment="反馈类型：like/dislike/rating")
    rating = Column(Integer, nullable=True, comment="评分（1-5星）")
    feedback_reason = Column(String(100), nullable=True, comment="反馈原因")
    comment = Column(Text, nullable=True, comment="详细评论")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="反馈时间")

    # 关联关系
    user = relationship("User")
    role = relationship("Role")
    message = relationship("ChatMessage")

    def __repr__(self):
        return f"<UserFeedback(user_id={self.user_id}, role_id={self.role_id}, type='{self.feedback_type}')>"


class RoleSkill(Base):
    __tablename__ = "role_skills"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, comment="角色ID")
    skill_name = Column(String(100), nullable=False, comment="技能名称")
    skill_description = Column(Text, nullable=True, comment="技能描述")
    skill_category = Column(String(50), nullable=True, comment="技能分类")
    proficiency_level = Column(Integer, default=0, comment="熟练度（0-100）")
    is_unlocked = Column(Boolean, default=False, comment="是否已解锁")
    unlock_level = Column(Integer, default=1, comment="解锁所需等级")
    usage_count = Column(Integer, default=0, comment="使用次数")
    skill_metadata = Column(JSON, nullable=True, comment="技能元数据")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关联关系
    role = relationship("Role")

    def __repr__(self):
        return f"<RoleSkill(role_id={self.role_id}, skill='{self.skill_name}', level={self.proficiency_level})>"