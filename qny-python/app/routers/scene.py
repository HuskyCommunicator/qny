from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import get_current_user_jwt
from ..models import User
from ..models.scene import SceneSession
from ..schemas.scene import (
    SceneTemplateCreate, SceneTemplateUpdate, SceneTemplateOut, SceneTemplateList,
    SceneSessionCreate, SceneSessionUpdate, SceneSessionOut, SceneSessionList,
    SceneParticipantCreate, SceneParticipantUpdate, SceneParticipantOut,
    SceneMessageCreate, SceneMessageOut,
    SceneMessageRequest, SceneResponse, SceneStats,
    SceneSessionDetail, SceneTemplateDetail
)
from ..services.scene_service import SceneService

router = APIRouter(prefix="/scene", tags=["多角色对话场景"])

@router.get("/templates", response_model=SceneTemplateList)
async def get_templates(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小"),
    scene_type: Optional[str] = Query(None, description="场景类型筛选"),
    db: Session = Depends(get_db)
):
    """获取场景模板列表"""
    service = SceneService(db)

    # 构建查询
    from ..models.scene import SceneTemplate
    query = db.query(SceneTemplate).filter(SceneTemplate.is_active == True)

    if scene_type:
        query = query.filter(SceneTemplate.scene_type == scene_type)

    # 分页
    offset = (page - 1) * size
    total = query.count()
    templates = query.order_by(SceneTemplate.created_at.desc()).offset(offset).limit(size).all()

    return SceneTemplateList(
        templates=templates,
        total=total,
        page=page,
        size=size
    )

@router.get("/templates/{template_id}", response_model=SceneTemplateDetail)
async def get_template_detail(template_id: int, db: Session = Depends(get_db)):
    """获取场景模板详情"""
    from ..models.scene import SceneTemplate, SceneInteractionRule

    template = db.query(SceneTemplate).filter(
        SceneTemplate.id == template_id,
        SceneTemplate.is_active == True
    ).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="场景模板不存在"
        )

    # 获取互动规则
    rules = db.query(SceneInteractionRule).filter(
        SceneInteractionRule.template_id == template_id,
        SceneInteractionRule.is_active == True
    ).all()

    return SceneTemplateDetail(
        **template.__dict__,
        interaction_rules=rules
    )

@router.post("/sessions", response_model=SceneSessionOut)
async def create_session(
    session_data: SceneSessionCreate,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """创建场景会话"""
    service = SceneService(db)

    try:
        session = service.create_session(current_user.id, session_data)
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sessions", response_model=SceneSessionList)
async def get_user_sessions(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页大小"),
    status: Optional[str] = Query(None, description="状态筛选"),
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """获取用户的场景会话列表"""
    service = SceneService(db)

    sessions, total = service.get_user_sessions(current_user.id, page, size)

    return SceneSessionList(
        sessions=sessions,
        total=total,
        page=page,
        size=size
    )

@router.get("/sessions/{session_id}", response_model=SceneSessionDetail)
async def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """获取场景会话详情"""
    service = SceneService(db)

    session = service.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
        )

    # 获取参与者
    participants = service.get_session_participants(session_id)

    # 获取最近的消息
    messages, _ = service.get_session_messages(session_id, 1, 20)

    return SceneSessionDetail(
        **session.__dict__,
        participants=participants,
        messages=messages
    )

@router.put("/sessions/{session_id}", response_model=SceneSessionOut)
async def update_session(
    session_id: int,
    session_data: SceneSessionUpdate,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """更新场景会话"""
    session = db.query(SceneSession).filter(
        SceneSession.id == session_id,
        SceneSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
        )

    # 更新字段
    update_data = session_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)

    db.commit()
    db.refresh(session)

    return session

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """删除场景会话"""
    service = SceneService(db)

    session = service.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
        )

    # 软删除 - 标记为已结束
    if service.end_session(session_id):
        return {"message": "会话已成功结束"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除会话失败"
        )

@router.post("/sessions/{session_id}/participants", response_model=SceneParticipantOut)
async def add_participant(
    session_id: int,
    participant_data: SceneParticipantCreate,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """添加场景参与者"""
    service = SceneService(db)

    # 验证会话权限
    session = service.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
        )

    try:
        participant = service.add_participant(session_id, participant_data)
        return participant
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sessions/{session_id}/participants", response_model=List[SceneParticipantOut])
async def get_session_participants(
    session_id: int,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """获取会话参与者列表"""
    service = SceneService(db)

    # 验证会话权限
    session = service.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
        )

    participants = service.get_session_participants(session_id)
    return participants

@router.delete("/sessions/{session_id}/participants/{participant_id}")
async def remove_participant(
    session_id: int,
    participant_id: int,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """移除场景参与者"""
    service = SceneService(db)

    # 验证会话权限
    session = service.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
        )

    if service.remove_participant(participant_id):
        return {"message": "参与者已成功移除"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="移除参与者失败"
        )

@router.post("/sessions/{session_id}/messages", response_model=SceneResponse)
async def send_scene_message(
    session_id: int,
    message_data: SceneMessageRequest,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """发送场景消息"""
    service = SceneService(db)

    # 设置会话ID
    message_data.session_id = session_id

    try:
        response = service.send_message(current_user.id, message_data)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sessions/{session_id}/messages", response_model=List[SceneMessageOut])
async def get_session_messages(
    session_id: int,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(50, ge=1, le=200, description="每页大小"),
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """获取会话消息历史"""
    service = SceneService(db)

    # 验证会话权限
    session = service.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
    )

    messages, total = service.get_session_messages(session_id, page, size)
    return messages

@router.get("/stats", response_model=SceneStats)
async def get_scene_stats(
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """获取场景统计信息"""
    service = SceneService(db)
    return service.get_scene_stats(current_user.id)

@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: int,
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """结束场景会话"""
    service = SceneService(db)

    # 验证会话权限
    session = service.get_session(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权限"
        )

    if service.end_session(session_id):
        return {"message": "会话已成功结束"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束会话失败"
        )

@router.get("/templates/types")
async def get_scene_types():
    """获取可用的场景类型"""
    return {
        "types": [
            {"value": "discussion", "label": "讨论场景"},
            {"value": "teaching", "label": "教学场景"},
            {"value": "debate", "label": "辩论场景"},
            {"value": "collaboration", "label": "协作场景"},
            {"value": "entertainment", "label": "娱乐场景"}
        ]
    }

@router.get("/templates/recommended")
async def get_recommended_templates(
    limit: int = Query(5, ge=1, le=10, description="推荐数量"),
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """获取推荐的场景模板"""
    from ..models.scene import SceneTemplate

    # 简单的推荐逻辑：返回最热门的模板
    templates = db.query(SceneTemplate).filter(
        SceneTemplate.is_active == True
    ).order_by(SceneTemplate.created_at.desc()).limit(limit).all()

    return {"templates": templates}

@router.post("/templates/initialize")
async def initialize_templates(
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """初始化场景模板数据"""
    service = SceneService(db)

    try:
        service.initialize_templates()
        return {"message": "场景模板初始化成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化失败: {str(e)}"
        )

# 场景推荐接口
@router.get("/recommendations")
async def get_scene_recommendations(
    current_user: User = Depends(get_current_user_jwt),
    db: Session = Depends(get_db)
):
    """获取场景推荐"""
    service = SceneService(db)

    # 获取用户统计信息
    stats = service.get_scene_stats(current_user.id)

    # 基于用户行为生成推荐
    recommendations = []

    # 如果用户没有使用过任何场景，推荐热门模板
    if stats.total_sessions == 0:
        from ..models.scene import SceneTemplate
        popular_templates = db.query(SceneTemplate).filter(
            SceneTemplate.is_active == True
        ).limit(3).all()

        for template in popular_templates:
            recommendations.append({
                "template": template,
                "reason": "热门推荐",
                "score": 0.8
            })

    return {"recommendations": recommendations}