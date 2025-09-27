from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# 枚举定义
class SceneType(str, Enum):
    DISCUSSION = "discussion"
    TEACHING = "teaching"
    DEBATE = "debate"
    COLLABORATION = "collaboration"
    ENTERTAINMENT = "entertainment"

class SceneStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"

class ParticipantType(str, Enum):
    AI = "ai"
    USER = "user"

class MessageType(str, Enum):
    TEXT = "text"
    SYSTEM = "system"
    ACTION = "action"

# 场景模板相关
class SceneTemplateBase(BaseModel):
    name: str = Field(..., description="模板名称")
    title: str = Field(..., description="场景标题")
    description: Optional[str] = Field(None, description="场景描述")
    scene_type: SceneType = Field(..., description="场景类型")
    max_roles: int = Field(3, description="最大角色数量")
    min_roles: int = Field(2, description="最小角色数量")
    config: Optional[Dict[str, Any]] = Field(None, description="场景配置")

class SceneTemplateCreate(SceneTemplateBase):
    pass

class SceneTemplateUpdate(BaseModel):
    title: Optional[str] = Field(None, description="场景标题")
    description: Optional[str] = Field(None, description="场景描述")
    max_roles: Optional[int] = Field(None, description="最大角色数量")
    min_roles: Optional[int] = Field(None, description="最小角色数量")
    config: Optional[Dict[str, Any]] = Field(None, description="场景配置")
    is_active: Optional[bool] = Field(None, description="是否启用")

class SceneTemplateOut(SceneTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 场景会话相关
class SceneSessionBase(BaseModel):
    name: str = Field(..., description="会话名称")
    description: Optional[str] = Field(None, description="会话描述")
    template_id: int = Field(..., description="模板ID")
    config: Optional[Dict[str, Any]] = Field(None, description="会话配置")

class SceneSessionCreate(SceneSessionBase):
    pass

class SceneSessionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="会话名称")
    description: Optional[str] = Field(None, description="会话描述")
    status: Optional[SceneStatus] = Field(None, description="会话状态")
    current_speaker: Optional[int] = Field(None, description="当前发言角色ID")
    config: Optional[Dict[str, Any]] = Field(None, description="会话配置")

class SceneSessionOut(SceneSessionBase):
    id: int
    session_id: str
    user_id: int
    status: SceneStatus
    current_speaker: Optional[int]
    message_count: int
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True

# 场景参与者相关
class SceneParticipantBase(BaseModel):
    session_id: int = Field(..., description="会话ID")
    role_id: int = Field(..., description="角色ID")
    participant_type: ParticipantType = Field(ParticipantType.AI, description="参与者类型")
    join_order: int = Field(1, description="加入顺序")
    personality_config: Optional[Dict[str, Any]] = Field(None, description="个性化配置")

class SceneParticipantCreate(BaseModel):
    role_id: int = Field(..., description="角色ID")
    participant_type: ParticipantType = Field(ParticipantType.AI, description="参与者类型")
    join_order: int = Field(1, description="加入顺序")
    personality_config: Optional[Dict[str, Any]] = Field(None, description="个性化配置")

class SceneParticipantUpdate(BaseModel):
    is_active: Optional[bool] = Field(None, description="是否活跃")
    personality_config: Optional[Dict[str, Any]] = Field(None, description="个性化配置")

class SceneParticipantOut(SceneParticipantBase):
    id: int
    is_active: bool
    speak_count: int
    last_speak_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# 场景消息相关
class SceneMessageBase(BaseModel):
    session_id: int = Field(..., description="会话ID")
    participant_id: Optional[int] = Field(None, description="参与者ID")
    role_id: int = Field(..., description="角色ID")
    message_type: MessageType = Field(MessageType.TEXT, description="消息类型")
    content: str = Field(..., description="消息内容")
    target_participant_id: Optional[int] = Field(None, description="目标参与者ID")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class SceneMessageCreate(SceneMessageBase):
    pass

class SceneMessageOut(SceneMessageBase):
    id: int
    message_order: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

# 场景互动规则相关
class SceneInteractionRuleBase(BaseModel):
    template_id: int = Field(..., description="模板ID")
    name: str = Field(..., description="规则名称")
    rule_type: str = Field(..., description="规则类型")
    condition: Optional[Dict[str, Any]] = Field(None, description="触发条件")
    action: Optional[Dict[str, Any]] = Field(None, description="执行动作")
    priority: int = Field(1, description="优先级")
    description: Optional[str] = Field(None, description="规则描述")

class SceneInteractionRuleCreate(SceneInteractionRuleBase):
    pass

class SceneInteractionRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, description="规则名称")
    rule_type: Optional[str] = Field(None, description="规则类型")
    condition: Optional[Dict[str, Any]] = Field(None, description="触发条件")
    action: Optional[Dict[str, Any]] = Field(None, description="执行动作")
    priority: Optional[int] = Field(None, description="优先级")
    is_active: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="规则描述")

class SceneInteractionRuleOut(SceneInteractionRuleBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# 场景推荐相关
class SceneRecommendationBase(BaseModel):
    template_id: int = Field(..., description="模板ID")
    score: float = Field(0.0, description="推荐分数")
    reason: Optional[str] = Field(None, description="推荐原因")

class SceneRecommendationCreate(SceneRecommendationBase):
    pass

class SceneRecommendationOut(SceneRecommendationBase):
    id: int
    user_id: int
    is_clicked: bool
    is_used: bool
    created_at: datetime

    class Config:
        from_attributes = True

# 复杂输出结构
class SceneSessionDetail(SceneSessionOut):
    template: SceneTemplateOut
    participants: List[SceneParticipantOut]
    messages: List[SceneMessageOut]

class SceneTemplateDetail(SceneTemplateOut):
    interaction_rules: List[SceneInteractionRuleOut]

class ParticipantInfo(BaseModel):
    id: int
    role_id: int
    role_name: str
    participant_type: ParticipantType
    speak_count: int
    is_active: bool

class SceneMessageDetail(SceneMessageOut):
    participant: Optional[ParticipantInfo]
    target_participant: Optional[ParticipantInfo]

# 请求和响应模型
class SceneMessageRequest(BaseModel):
    session_id: int = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    target_role_id: Optional[int] = Field(None, description="目标角色ID")
    message_type: MessageType = Field(MessageType.TEXT, description="消息类型")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class SceneResponse(BaseModel):
    session_id: int
    messages: List[SceneMessageDetail]
    current_speaker: Optional[int]
    speaker_rotation: List[int]
    suggestions: Optional[List[str]] = Field(None, description="建议的回复")

class SceneStats(BaseModel):
    total_sessions: int
    active_sessions: int
    total_messages: int
    popular_templates: List[Dict[str, Any]]
    role_participation: List[Dict[str, Any]]

class SceneRecommendationResponse(BaseModel):
    recommendations: List[SceneRecommendationOut]
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="用户偏好")

# 分页相关
class SceneSessionList(BaseModel):
    sessions: List[SceneSessionOut]
    total: int
    page: int
    size: int

class SceneTemplateList(BaseModel):
    templates: List[SceneTemplateOut]
    total: int
    page: int
    size: int