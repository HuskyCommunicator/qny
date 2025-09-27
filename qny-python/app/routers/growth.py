"""
成长系统API路由
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from datetime import datetime

from ..core.security import get_current_user
from ..core.db import get_db
from ..models import User, Role, RoleSkill, UserFeedback
from ..schemas.growth import (
    FeedbackCreate, FeedbackResponse, RoleGrowthSummary, FeedbackAnalysis,
    RoleSkillResponse, GrowthLeaderboard, FeedbackReasonOptions,
    SkillUpdateResponse, UserFeedbackStats, GrowthStats, FeedbackReason,
    LevelInfo, SkillProgress, GrowthHistory
)
from ..services.growth_service import GrowthService

router = APIRouter(prefix="/growth", tags=["growth"])


@router.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(
    feedback: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建用户反馈
    """
    growth_service = GrowthService(db)

    success = growth_service.record_feedback(
        user_id=current_user.id,
        role_id=feedback.role_id,
        message_id=feedback.message_id,
        feedback_type=feedback.feedback_type,
        rating=feedback.rating,
        feedback_reason=feedback.feedback_reason,
        comment=feedback.comment
    )

    if not success:
        raise HTTPException(status_code=400, detail="反馈创建失败")

    # 返回创建的反馈信息
    created_feedback = db.query(UserFeedback).filter(
        UserFeedback.user_id == current_user.id,
        UserFeedback.role_id == feedback.role_id
    ).order_by(UserFeedback.created_at.desc()).first()

    return FeedbackResponse(
        id=created_feedback.id,
        user_id=created_feedback.user_id,
        role_id=created_feedback.role_id,
        message_id=created_feedback.message_id,
        feedback_type=created_feedback.feedback_type,
        rating=created_feedback.rating,
        feedback_reason=created_feedback.feedback_reason,
        comment=created_feedback.comment,
        created_at=created_feedback.created_at
    )


@router.get("/role/{role_id}/summary", response_model=RoleGrowthSummary)
async def get_role_growth_summary(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色成长摘要
    """
    growth_service = GrowthService(db)
    summary = growth_service.get_role_growth_summary(role_id)

    if not summary:
        raise HTTPException(status_code=404, detail="角色不存在")

    return summary


@router.get("/role/{role_id}/skills", response_model=List[RoleSkillResponse])
async def get_role_skills(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色技能列表
    """
    skills = db.query(RoleSkill).filter(RoleSkill.role_id == role_id).all()

    return [
        RoleSkillResponse(
            id=skill.id,
            role_id=skill.role_id,
            skill_name=skill.skill_name,
            skill_description=skill.skill_description,
            skill_category=skill.skill_category,
            proficiency_level=skill.proficiency_level,
            is_unlocked=skill.is_unlocked,
            unlock_level=skill.unlock_level,
            usage_count=skill.usage_count,
            skill_metadata=skill.skill_metadata,
            created_at=skill.created_at
        )
        for skill in skills
    ]


@router.get("/my/feedback-analysis", response_model=FeedbackAnalysis)
async def get_my_feedback_analysis(
    role_id: Optional[int] = Query(None, description="指定角色ID，不指定则分析所有角色"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户的反馈分析
    """
    growth_service = GrowthService(db)
    analysis = growth_service.get_user_feedback_analysis(current_user.id, role_id)

    return analysis


@router.get("/leaderboard", response_model=List[GrowthLeaderboard])
async def get_growth_leaderboard(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    sort_by: str = Query("experience", description="排序字段：experience/level/satisfaction_rate"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取成长排行榜
    """
    # 查询活跃角色（有对话记录的角色）
    query = db.query(Role).filter(Role.total_conversations > 0)

    # 排序
    if sort_by == "level":
        query = query.order_by(Role.level.desc(), Role.experience.desc())
    elif sort_by == "satisfaction_rate":
        # 计算满意度并排序
        query = query.order_by(
            (Role.positive_feedback * 1.0 /
             (Role.positive_feedback + Role.negative_feedback + 1)).desc(),
            Role.level.desc()
        )
    else:  # experience
        query = query.order_by(Role.experience.desc(), Role.level.desc())

    roles = query.limit(limit).all()

    leaderboard = []
    for rank, role in enumerate(roles, 1):
        satisfaction_rate = 0
        if role.positive_feedback + role.negative_feedback > 0:
            satisfaction_rate = (role.positive_feedback /
                              (role.positive_feedback + role.negative_feedback)) * 100

        leaderboard.append(GrowthLeaderboard(
            role_id=role.id,
            role_name=role.name,
            level=role.level,
            experience=role.experience,
            total_conversations=role.total_conversations,
            satisfaction_rate=satisfaction_rate,
            rank=rank
        ))

    return leaderboard


@router.get("/feedback-reasons", response_model=FeedbackReasonOptions)
async def get_feedback_reasons():
    """
    获取反馈原因选项
    """
    like_reasons = [
        FeedbackReason(reason="回复很有帮助", category="有用性"),
        FeedbackReason(reason="回答准确", category="准确性"),
        FeedbackReason(reason="解释清晰", category="清晰度"),
        FeedbackReason(reason="回复及时", category="及时性"),
        FeedbackReason(reason="态度友好", category="态度"),
        FeedbackReason(reason="专业知识强", category="专业性")
    ]

    dislike_reasons = [
        FeedbackReason(reason="回答不准确", category="准确性"),
        FeedbackReason(reason="理解错误", category="理解度"),
        FeedbackReason(reason="回复不相关", category="相关性"),
        FeedbackReason(reason="解释不清楚", category="清晰度"),
        FeedbackReason(reason="态度生硬", category="态度"),
        FeedbackReason(reason="重复回答", category="重复性")
    ]

    rating_reasons = [
        FeedbackReason(reason="专业性强", category="专业性"),
        FeedbackReason(reason="回答全面", category="全面性"),
        FeedbackReason(reason="逻辑清晰", category="逻辑性"),
        FeedbackReason(reason="实用性强", category="实用性"),
        FeedbackReason(reason="需要改进", category="改进建议"),
        FeedbackReason(reason="有待提高", category="提高建议")
    ]

    return FeedbackReasonOptions(
        like_reasons=like_reasons,
        dislike_reasons=dislike_reasons,
        rating_reasons=rating_reasons
    )


@router.get("/my/stats", response_model=UserFeedbackStats)
async def get_my_feedback_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户反馈统计
    """
    # 统计用户反馈
    feedbacks = db.query(UserFeedback).filter(UserFeedback.user_id == current_user.id).all()

    total_given = len(feedbacks)
    satisfaction_score = 0

    for feedback in feedbacks:
        if feedback.feedback_type == 'like':
            satisfaction_score += 5
        elif feedback.feedback_type == 'dislike':
            satisfaction_score += 1
        elif feedback.rating:
            satisfaction_score += feedback.rating

    satisfaction_rate = (satisfaction_score / (total_given * 5)) * 100 if total_given > 0 else 75.0

    # 统计最喜欢的角色
    favorite_roles_query = db.query(
        Role.id,
        Role.name,
        UserFeedback.feedback_type,
        UserFeedback.rating
    ).join(UserFeedback).filter(UserFeedback.user_id == current_user.id).all()

    role_scores = {}
    for role_id, role_name, feedback_type, rating in favorite_roles_query:
        if role_id not in role_scores:
            role_scores[role_id] = {'name': role_name, 'score': 0, 'count': 0}

        if feedback_type == 'like':
            role_scores[role_id]['score'] += 5
        elif feedback_type == 'dislike':
            role_scores[role_id]['score'] += 1
        elif rating:
            role_scores[role_id]['score'] += rating

        role_scores[role_id]['count'] += 1

    favorite_roles = sorted(
        [{'role_id': rid, **data} for rid, data in role_scores.items()],
        key=lambda x: x['score'],
        reverse=True
    )[:5]

    # 趋势分析
    trend = "反馈积极" if satisfaction_rate > 70 else "反馈一般" if satisfaction_rate > 50 else "需要改进"

    return UserFeedbackStats(
        total_given=total_given,
        satisfaction_rate=satisfaction_rate,
        favorite_roles=favorite_roles,
        feedback_trend=trend
    )


@router.post("/role/{role_id}/skill/{skill_name}/use", response_model=SkillUpdateResponse)
async def use_role_skill(
    role_id: int,
    skill_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    使用角色技能并更新熟练度
    """
    growth_service = GrowthService(db)

    # 获取当前熟练度
    skill = db.query(RoleSkill).filter(
        RoleSkill.role_id == role_id,
        RoleSkill.skill_name == skill_name
    ).first()

    if not skill:
        raise HTTPException(status_code=404, detail="技能不存在")

    old_proficiency = skill.proficiency_level

    # 更新熟练度
    success = growth_service.update_skill_proficiency(role_id, skill_name)

    if not success:
        raise HTTPException(status_code=400, detail="技能更新失败")

    # 获取更新后的技能
    updated_skill = db.query(RoleSkill).filter(
        RoleSkill.role_id == role_id,
        RoleSkill.skill_name == skill_name
    ).first()

    exp_gained = updated_skill.proficiency_level - old_proficiency

    return SkillUpdateResponse(
        skill_name=skill_name,
        old_proficiency=old_proficiency,
        new_proficiency=updated_skill.proficiency_level,
        usage_count=updated_skill.usage_count,
        exp_gained=exp_gained
    )


@router.get("/role/{role_id}/stats", response_model=GrowthStats)
async def get_role_growth_stats(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色成长统计
    """
    try:
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")

        # 计算下一级所需经验值
        growth_service = GrowthService(db)
        next_level_exp = growth_service.calculate_experience_for_next_level(role.level)
        current_level_exp = ((role.level - 1) ** 2) * 100
        exp_progress = role.experience - current_level_exp
        exp_needed = next_level_exp - current_level_exp
        progress_percentage = (exp_progress / exp_needed * 100) if exp_needed > 0 else 0

        level_info = LevelInfo(
            current_level=role.level,
            current_exp=role.experience,
            next_level_exp=next_level_exp,
            exp_progress=exp_progress,
            exp_needed=exp_needed,
            progress_percentage=progress_percentage
        )

        # 获取顶级技能，去重处理避免重复数据
        skill_names = db.query(distinct(RoleSkill.skill_name)).filter(
            RoleSkill.role_id == role_id,
            RoleSkill.is_unlocked == True
        ).all()

        skill_progress = []
        for skill_name_result in skill_names:
            skill_name = skill_name_result[0]
            # 获取该技能的最新记录
            skill = db.query(RoleSkill).filter(
                RoleSkill.role_id == role_id,
                RoleSkill.skill_name == skill_name,
                RoleSkill.is_unlocked == True
            ).order_by(RoleSkill.created_at.desc()).first()

            if skill:
                skill_progress.append(SkillProgress(
                    skill_name=skill.skill_name,
                    skill_description=skill.skill_description,
                    proficiency_level=skill.proficiency_level,
                    is_unlocked=skill.is_unlocked,
                    unlock_level=skill.unlock_level,
                    usage_count=skill.usage_count
                ))

        # 最近活动（从growth_stats中获取）
        recent_activities = []
        if role.growth_stats and isinstance(role.growth_stats, dict) and 'history' in role.growth_stats:
            try:
                history_data = role.growth_stats['history']
                if isinstance(history_data, list):
                    for activity in history_data[-10:]:  # 最近10条
                        try:
                            recent_activities.append(GrowthHistory(
                                timestamp=activity.get('timestamp', datetime.now()),
                                event_type=activity.get('event_type', 'unknown'),
                                description=activity.get('description', ''),
                                metadata=activity.get('metadata', {})
                            ))
                        except Exception:
                            # 如果单个活动项有问题，跳过
                            continue
            except Exception:
                # 如果解析历史数据有问题，设为空列表
                recent_activities = []

        # 计算满意度，添加错误处理
        try:
            satisfaction_rate = growth_service._calculate_satisfaction_rate(role)
        except Exception as e:
            satisfaction_rate = 75.0  # 默认值

        # 计算成长率，添加错误处理
        try:
            growth_rate = growth_service._calculate_growth_rate(role)
        except Exception as e:
            growth_rate = 0.0  # 默认值

        return GrowthStats(
            role_id=role.id,
            total_conversations=role.total_conversations or 0,
            total_feedbacks=(role.positive_feedback or 0) + (role.negative_feedback or 0),
            satisfaction_rate=satisfaction_rate,
            growth_rate=growth_rate,
            level_progress=level_info,
            top_skills=skill_progress,
            recent_activities=recent_activities
        )

    except HTTPException:
        raise
    except Exception as e:
        # 捕获所有其他异常并返回500错误
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )