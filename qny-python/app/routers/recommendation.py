"""
推荐系统API路由
提供智能角色推荐相关的接口
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from ..core.db import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..schemas.recommendation import (
    RecommendationResponse, UserBehaviorProfile,
    RecommendationExplanation, RecommendationAnalytics
)
from ..services.recommendation_service import get_recommendation_engine, RecommendationEngine

router = APIRouter(prefix="/recommendation", tags=["recommendation"])


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationEngine:
    """获取推荐服务实例"""
    return get_recommendation_engine(db)


@router.get("/roles", response_model=RecommendationResponse)
def get_role_recommendations(
    algorithm: str = Query("hybrid", description="推荐算法类型: collaborative, content, popular, hybrid"),
    limit: int = Query(8, ge=1, le=20, description="推荐数量限制"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    recommendation_service: RecommendationEngine = Depends(get_recommendation_service)
):
    """获取角色推荐"""
    try:
        user_id = current_user.id

        # 根据算法类型获取推荐
        if algorithm == "collaborative":
            recommendations_data = recommendation_service.get_collaborative_recommendations(user_id, limit)
        elif algorithm == "content":
            recommendations_data = recommendation_service.get_content_based_recommendations(user_id, limit)
        elif algorithm == "popular":
            recommendations_data = recommendation_service.get_popular_roles(limit)
        else:  # hybrid
            recommendations_data = recommendation_service.get_hybrid_recommendations(user_id, limit)

        # 转换为响应格式
        from ..schemas.recommendation import RecommendationItem
        from ..schemas.role import RoleOut

        recommendation_items = []
        for rec_data in recommendations_data:
            role_out = RoleOut.from_orm(rec_data["role"])
            recommendation_item = RecommendationItem(
                role=role_out,
                score=rec_data["score"],
                reason=rec_data["reason"]
            )
            recommendation_items.append(recommendation_item)

        # 获取用户画像摘要
        user_profile = recommendation_service.get_user_behavior_analysis(user_id)
        profile_summary = {
            "total_sessions": user_profile["total_sessions"],
            "favorite_categories": user_profile["favorite_categories"][:3],
            "favorite_tags": user_profile["favorite_tags"][:5]
        }

        return RecommendationResponse(
            recommendations=recommendation_items,
            total_count=len(recommendation_items),
            algorithm_used=algorithm,
            user_profile_summary=profile_summary
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐失败: {str(e)}"
        )


@router.get("/profile", response_model=UserBehaviorProfile)
def get_user_behavior_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    recommendation_service: RecommendationEngine = Depends(get_recommendation_service)
):
    """获取用户行为画像"""
    try:
        user_id = current_user.id
        user_profile = recommendation_service.get_user_behavior_analysis(user_id)

        return UserBehaviorProfile(
            user_id=user_profile["user_id"],
            total_sessions=user_profile["total_sessions"],
            total_messages=user_profile["total_messages"],
            activity_level=user_profile["activity_level"],
            favorite_categories=user_profile["favorite_categories"],
            favorite_tags=user_profile["favorite_tags"],
            most_used_roles=user_profile["most_used_roles"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户画像失败: {str(e)}"
        )


@router.get("/explain/{role_id}", response_model=RecommendationExplanation)
def get_recommendation_explanation(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    recommendation_service: RecommendationEngine = Depends(get_recommendation_service)
):
    """获取推荐解释"""
    try:
        user_id = current_user.id
        explanation = recommendation_service.get_recommendation_explanation(user_id, role_id)

        return RecommendationExplanation(
            role_name=explanation["role_name"],
            reasons=explanation["reasons"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐解释失败: {str(e)}"
        )


@router.get("/analytics", response_model=RecommendationAnalytics)
def get_recommendation_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    recommendation_service: RecommendationEngine = Depends(get_recommendation_service)
):
    """获取推荐分析数据"""
    try:
        # 获取热门角色统计
        popular_roles_data = recommendation_service.get_popular_roles(10)

        # 简化的分析数据 (实际项目中可以从数据库统计)
        analytics_data = RecommendationAnalytics(
            total_recommendations=150,  # 示例数据
            click_through_rate=0.25,     # 示例数据
            popular_roles=[
                {
                    "role_id": rec["role"].id,
                    "role_name": rec["role"].name,
                    "usage_count": rec["score"]
                }
                for rec in popular_roles_data
            ],
            user_satisfaction=0.84        # 示例数据 (4.2/5.0 归一化到0-1范围)
        )

        return analytics_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐分析失败: {str(e)}"
        )


@router.post("/track/{role_id}")
def track_role_interaction(
    role_id: int,
    interaction_type: str = Query("click", description="交互类型: click, chat, favorite"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    recommendation_service: RecommendationEngine = Depends(get_recommendation_service)
):
    """追踪用户与角色的交互"""
    try:
        user_id = current_user.id
        recommendation_service.track_user_interaction(user_id, role_id, interaction_type)

        return {"message": "交互追踪成功", "role_id": role_id, "interaction_type": interaction_type}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"追踪交互失败: {str(e)}"
        )