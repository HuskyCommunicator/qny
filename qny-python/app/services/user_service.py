"""
用户服务模块
- 用户管理
- 用户偏好设置
- 用户行为分析
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import json

from ..models import User, ChatSession, UserFeedback, UserRole
from ..schemas.user import UserPreferences, UserProfile, UserActivityStats
from ..core.exceptions import NotFoundError, ValidationError
from ..utils.helpers import validate_email, validate_password, calculate_age


class UserService:
    """用户服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """获取用户详细信息"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户不存在")

        # 获取用户统计信息
        stats = self._get_user_stats(user_id)
        preferences = self._get_user_preferences(user_id)
        activity = self._get_user_activity(user_id)

        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar": user.avatar,
            "bio": user.bio,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active,
            "preferences": preferences,
            "stats": stats,
            "activity": activity
        }

    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """更新用户资料"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户不存在")

        try:
            # 允许更新的字段
            updatable_fields = ['username', 'email', 'avatar', 'bio', 'preferences']

            for field, value in profile_data.items():
                if field in updatable_fields and hasattr(user, field):
                    if field == 'email':
                        if not validate_email(value):
                            raise ValidationError("邮箱格式不正确")
                    if field == 'preferences':
                        # 验证偏好设置格式
                        if not isinstance(value, dict):
                            raise ValidationError("偏好设置必须是字典格式")
                        user.preferences = json.dumps(value, ensure_ascii=False)
                    else:
                        setattr(user, field, value)

            user.updated_at = datetime.now()
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise e

    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """更新用户偏好设置"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户不存在")

        try:
            # 验证偏好设置
            validated_preferences = self._validate_preferences(preferences)
            user.preferences = json.dumps(validated_preferences, ensure_ascii=False)
            user.updated_at = datetime.now()
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise e

    def get_user_activity_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """获取用户活动统计"""
        start_date = datetime.now() - timedelta(days=days)

        # 聊天活动统计
        chat_stats = self.db.query(
            func.count(ChatSession.id).label('total_sessions'),
            func.sum(ChatSession.message_count).label('total_messages'),
            func.avg(ChatSession.message_count).label('avg_messages_per_session')
        ).filter(
            and_(
                ChatSession.user_id == user_id,
                ChatSession.created_at >= start_date
            )
        ).first()

        # 反馈活动统计
        feedback_stats = self.db.query(
            func.count(UserFeedback.id).label('total_feedback'),
            func.avg(UserFeedback.rating).label('avg_rating')
        ).filter(
            and_(
                UserFeedback.user_id == user_id,
                UserFeedback.created_at >= start_date
            )
        ).first()

        # 每日活动趋势
        daily_activity = self._get_daily_activity(user_id, days)

        return {
            "period_days": days,
            "chat_stats": {
                "total_sessions": chat_stats.total_sessions or 0,
                "total_messages": chat_stats.total_messages or 0,
                "avg_messages_per_session": round(chat_stats.avg_messages_per_session or 0, 2)
            },
            "feedback_stats": {
                "total_feedback": feedback_stats.total_feedback or 0,
                "avg_rating": round(feedback_stats.avg_rating or 0, 2)
            },
            "daily_activity": daily_activity
        }

    def get_user_recommendation_settings(self, user_id: int) -> Dict[str, Any]:
        """获取用户推荐设置"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户不存在")

        default_settings = {
            "enable_recommendations": True,
            "recommendation_algorithm": "hybrid",
            "max_recommendations": 8,
            "notification_frequency": "weekly",
            "privacy_settings": {
                "share_activity": True,
                "share_preferences": False
            }
        }

        try:
            if user.preferences:
                user_prefs = json.loads(user.preferences)
                return user_prefs.get('recommendation_settings', default_settings)
            return default_settings
        except (json.JSONDecodeError, TypeError):
            return default_settings

    def update_recommendation_settings(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """更新用户推荐设置"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundError("用户不存在")

        try:
            # 验证设置
            validated_settings = self._validate_recommendation_settings(settings)

            # 获取现有偏好设置
            current_prefs = {}
            if user.preferences:
                try:
                    current_prefs = json.loads(user.preferences)
                except json.JSONDecodeError:
                    pass

            # 更新推荐设置
            current_prefs['recommendation_settings'] = validated_settings
            user.preferences = json.dumps(current_prefs, ensure_ascii=False)
            user.updated_at = datetime.now()
            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise e

    def get_user_favorites(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户收藏的角色"""
        user_roles = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_favorite == True
            )
        ).all()

        favorites = []
        for user_role in user_roles:
            if user_role.role:
                favorites.append({
                    "role_id": user_role.role_id,
                    "role_name": user_role.role.name,
                    "role_avatar": user_role.role.avatar,
                    "added_at": user_role.created_at.isoformat(),
                    "usage_count": user_role.usage_count or 0
                })

        return favorites

    def add_to_favorites(self, user_id: int, role_id: int) -> bool:
        """添加角色到收藏"""
        user_role = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        ).first()

        if not user_role:
            # 创建新的用户角色关联
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                is_favorite=True,
                created_at=datetime.now()
            )
            self.db.add(user_role)
        else:
            user_role.is_favorite = True
            user_role.updated_at = datetime.now()

        self.db.commit()
        return True

    def remove_from_favorites(self, user_id: int, role_id: int) -> bool:
        """从收藏中移除角色"""
        user_role = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            )
        ).first()

        if user_role:
            user_role.is_favorite = False
            user_role.updated_at = datetime.now()
            self.db.commit()
            return True

        return False

    def get_user_insights(self, user_id: int) -> Dict[str, Any]:
        """获取用户洞察"""
        # 获取用户行为分析
        user_sessions = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).all()

        if not user_sessions:
            return {"message": "暂无足够数据生成用户洞察"}

        # 分析用户偏好
        role_preferences = {}
        time_preferences = {"morning": 0, "afternoon": 0, "evening": 0, "night": 0}
        day_preferences = {}

        for session in user_sessions:
            if session.role_id:
                role_preferences[session.role_id] = role_preferences.get(session.role_id, 0) + 1

            if session.created_at:
                hour = session.created_at.hour
                if 6 <= hour < 12:
                    time_preferences["morning"] += 1
                elif 12 <= hour < 18:
                    time_preferences["afternoon"] += 1
                elif 18 <= hour < 24:
                    time_preferences["evening"] += 1
                else:
                    time_preferences["night"] += 1

                day_of_week = session.created_at.strftime("%A")
                day_preferences[day_of_week] = day_preferences.get(day_of_week, 0) + 1

        # 获取最常用的角色
        most_used_role_id = max(role_preferences, key=role_preferences.get) if role_preferences else None
        most_used_role_name = None
        if most_used_role_id:
            role = self.db.query(User).filter(User.id == most_used_role_id).first()
            most_used_role_name = role.username if role else None

        # 获取最活跃的时间段
        most_active_time = max(time_preferences, key=time_preferences.get) if time_preferences else None
        most_active_day = max(day_preferences, key=day_preferences.get) if day_preferences else None

        return {
            "total_sessions": len(user_sessions),
            "most_used_role": {
                "role_id": most_used_role_id,
                "role_name": most_used_role_name
            },
            "activity_patterns": {
                "time_preferences": time_preferences,
                "day_preferences": day_preferences,
                "most_active_time": most_active_time,
                "most_active_day": most_active_day
            },
            "engagement_level": self._calculate_engagement_level(len(user_sessions)),
            "recommendations": self._generate_user_recommendations(role_preferences, time_preferences)
        }

    def _get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """获取用户统计信息"""
        total_sessions = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).count()

        total_messages = self.db.query(func.sum(ChatSession.message_count)).filter(
            ChatSession.user_id == user_id
        ).scalar() or 0

        total_feedback = self.db.query(UserFeedback).filter(
            UserFeedback.user_id == user_id
        ).count()

        favorite_roles = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_favorite == True
            )
        ).count()

        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "total_feedback": total_feedback,
            "favorite_roles": favorite_roles
        }

    def _get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """获取用户偏好设置"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.preferences:
            return {}

        try:
            return json.loads(user.preferences)
        except json.JSONDecodeError:
            return {}

    def _get_user_activity(self, user_id: int) -> Dict[str, Any]:
        """获取用户最近活动"""
        recent_sessions = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(desc(ChatSession.created_at)).limit(5).all()

        recent_feedback = self.db.query(UserFeedback).filter(
            UserFeedback.user_id == user_id
        ).order_by(desc(UserFeedback.created_at)).limit(5).all()

        return {
            "recent_sessions": [
                {
                    "session_id": s.id,
                    "role_name": s.role.name if s.role else "Unknown",
                    "created_at": s.created_at.isoformat(),
                    "message_count": s.message_count or 0
                }
                for s in recent_sessions
            ],
            "recent_feedback": [
                {
                    "feedback_id": f.id,
                    "role_name": f.role.name if f.role else "Unknown",
                    "feedback_type": f.feedback_type,
                    "rating": f.rating,
                    "created_at": f.created_at.isoformat()
                }
                for f in recent_feedback
            ]
        }

    def _get_daily_activity(self, user_id: int, days: int) -> List[Dict[str, Any]]:
        """获取每日活动数据"""
        start_date = datetime.now() - timedelta(days=days)

        daily_stats = self.db.query(
            func.date(ChatSession.created_at).label('date'),
            func.count(ChatSession.id).label('sessions'),
            func.sum(ChatSession.message_count).label('messages')
        ).filter(
            and_(
                ChatSession.user_id == user_id,
                ChatSession.created_at >= start_date
            )
        ).group_by(func.date(ChatSession.created_at)).all()

        return [
            {
                "date": stat.date.isoformat(),
                "sessions": stat.sessions,
                "messages": stat.messages or 0
            }
            for stat in daily_stats
        ]

    def _validate_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """验证用户偏好设置"""
        validated = {}

        # 语言偏好
        if 'language' in preferences:
            validated['language'] = str(preferences['language'])

        # 主题偏好
        if 'theme' in preferences:
            validated['theme'] = str(preferences['theme'])

        # 通知设置
        if 'notifications' in preferences:
            validated['notifications'] = bool(preferences['notifications'])

        # 隐私设置
        if 'privacy' in preferences and isinstance(preferences['privacy'], dict):
            validated['privacy'] = preferences['privacy']

        return validated

    def _validate_recommendation_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """验证推荐设置"""
        validated = {}

        # 启用推荐
        if 'enable_recommendations' in settings:
            validated['enable_recommendations'] = bool(settings['enable_recommendations'])

        # 推荐算法
        valid_algorithms = ['collaborative', 'content', 'popular', 'hybrid']
        if 'recommendation_algorithm' in settings:
            algo = settings['recommendation_algorithm']
            if algo in valid_algorithms:
                validated['recommendation_algorithm'] = algo

        # 最大推荐数量
        if 'max_recommendations' in settings:
            max_rec = int(settings['max_recommendations'])
            validated['max_recommendations'] = max(1, min(20, max_rec))

        # 通知频率
        valid_frequencies = ['daily', 'weekly', 'monthly', 'never']
        if 'notification_frequency' in settings:
            freq = settings['notification_frequency']
            if freq in valid_frequencies:
                validated['notification_frequency'] = freq

        # 隐私设置
        if 'privacy_settings' in settings and isinstance(settings['privacy_settings'], dict):
            validated['privacy_settings'] = settings['privacy_settings']

        return validated

    def _calculate_engagement_level(self, session_count: int) -> str:
        """计算用户参与度等级"""
        if session_count >= 100:
            return "high"
        elif session_count >= 50:
            return "medium"
        elif session_count >= 20:
            return "low"
        else:
            return "new"

    def _generate_user_recommendations(self, role_preferences: Dict[int, int], time_preferences: Dict[str, int]) -> List[str]:
        """生成用户建议"""
        recommendations = []

        # 基于角色使用情况的建议
        if len(role_preferences) <= 2:
            recommendations.append("建议尝试更多不同类型的角色，丰富聊天体验")

        # 基于时间偏好的建议
        most_active_time = max(time_preferences, key=time_preferences.get) if time_preferences else None
        if most_active_time:
            time_map = {
                "morning": "早上",
                "afternoon": "下午",
                "evening": "晚上",
                "night": "夜间"
            }
            recommendations.append(f"您在{time_map[most_active_time]}最活跃，建议在这个时间段进行重要对话")

        return recommendations