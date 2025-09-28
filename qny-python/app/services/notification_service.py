"""
通知服务模块
- 用户通知管理
- 系统通知
- 推送通知
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import json
from dataclasses import dataclass
from enum import Enum

from ..models import User, Role, ChatSession
from ..core.exceptions import ValidationError


class NotificationType(Enum):
    """通知类型"""
    SYSTEM = "system"
    RECOMMENDATION = "recommendation"
    GROWTH = "growth"
    ACTIVITY = "activity"
    FEEDBACK = "feedback"
    MAINTENANCE = "maintenance"


class NotificationPriority(Enum):
    """通知优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationConfig:
    """通知配置"""
    MAX_NOTIFICATIONS_PER_USER: int = 100
    NOTIFICATION_TTL_DAYS: int = 30
    CLEANUP_INTERVAL_HOURS: int = 24


class NotificationService:
    """通知服务"""

    def __init__(self, db: Session, config: Optional[NotificationConfig] = None):
        self.db = db
        self.config = config or NotificationConfig()

    def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict[str, Any]] = None,
        is_system: bool = False
    ) -> Dict[str, Any]:
        """创建通知"""
        # 检查通知限制
        if not is_system:
            user_notification_count = self._get_user_notification_count(user_id)
            if user_notification_count >= self.config.MAX_NOTIFICATIONS_PER_USER:
                self._cleanup_old_notifications(user_id)

        # 创建通知记录
        notification = {
            "user_id": user_id,
            "type": notification_type.value,
            "title": title,
            "message": message,
            "priority": priority.value,
            "data": json.dumps(data or {}, ensure_ascii=False),
            "is_read": False,
            "is_system": is_system,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(days=self.config.NOTIFICATION_TTL_DAYS)
        }

        # 这里应该创建Notification模型并保存到数据库
        # 由于我们项目中没有Notification模型，这里返回模拟数据
        notification_id = self._save_notification_to_db(notification)

        return {
            "notification_id": notification_id,
            "status": "created",
            "message": "通知创建成功"
        }

    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """获取用户通知列表"""
        # 构建查询条件
        filters = {"user_id": user_id}
        if unread_only:
            filters["is_read"] = False

        # 模拟查询结果
        notifications = self._query_notifications_from_db(filters, limit, offset)

        # 统计未读数量
        unread_count = self._count_unread_notifications(user_id)

        return {
            "notifications": notifications,
            "unread_count": unread_count,
            "total_count": len(notifications),
            "has_more": len(notifications) == limit
        }

    def mark_notification_read(self, user_id: int, notification_id: int) -> bool:
        """标记通知为已读"""
        # 模拟更新操作
        success = self._update_notification_read_status(notification_id, True)
        return success

    def mark_all_notifications_read(self, user_id: int) -> int:
        """标记所有通知为已读"""
        # 模拟批量更新操作
        updated_count = self._update_all_notifications_read_status(user_id)
        return updated_count

    def delete_notification(self, user_id: int, notification_id: int) -> bool:
        """删除通知"""
        success = self._delete_notification_from_db(notification_id, user_id)
        return success

    def create_growth_notification(self, user_id: int, role_id: int, event_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """创建成长相关通知"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValidationError("角色不存在")

        title = f"{role.name} 成长通知"
        message = self._generate_growth_message(event_type, details)

        data = {
            "event_type": event_type,
            "role_id": role_id,
            "role_name": role.name,
            "details": details
        }

        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.GROWTH,
            title=title,
            message=message,
            priority=NotificationPriority.MEDIUM,
            data=data
        )

    def create_recommendation_notification(self, user_id: int, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建推荐相关通知"""
        if not recommendations:
            return {"status": "skipped", "message": "无推荐内容"}

        title = "为您推荐新的角色"
        message = f"根据您的使用偏好，我们为您推荐了 {len(recommendations)} 个新角色"

        data = {
            "recommendations": recommendations,
            "recommendation_count": len(recommendations)
        }

        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.RECOMMENDATION,
            title=title,
            message=message,
            priority=NotificationPriority.LOW,
            data=data
        )

    def create_activity_notification(self, user_id: int, activity_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """创建活动相关通知"""
        title = self._generate_activity_title(activity_type, details)
        message = self._generate_activity_message(activity_type, details)

        data = {
            "activity_type": activity_type,
            "details": details
        }

        priority = NotificationPriority.MEDIUM
        if activity_type in ["achievement", "milestone"]:
            priority = NotificationPriority.HIGH

        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.ACTIVITY,
            title=title,
            message=message,
            priority=priority,
            data=data
        )

    def create_system_notification(self, user_ids: List[int], title: str, message: str, priority: NotificationPriority = NotificationPriority.HIGH) -> List[Dict[str, Any]]:
        """创建系统通知"""
        results = []
        for user_id in user_ids:
            result = self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.SYSTEM,
                title=title,
                message=message,
                priority=priority,
                is_system=True
            )
            results.append(result)

        return results

    def create_maintenance_notification(self, start_time: datetime, duration: int, description: str) -> Dict[str, Any]:
        """创建系统维护通知"""
        title = "系统维护通知"
        message = f"系统将于 {start_time.strftime('%Y-%m-%d %H:%M')} 进行维护，预计耗时 {duration} 分钟"

        data = {
            "maintenance_start": start_time.isoformat(),
            "maintenance_duration": duration,
            "description": description
        }

        # 发送给所有活跃用户
        active_users = self._get_active_users()
        results = []

        for user in active_users:
            result = self.create_notification(
                user_id=user.id,
                notification_type=NotificationType.MAINTENANCE,
                title=title,
                message=message,
                priority=NotificationPriority.HIGH,
                data=data,
                is_system=True
            )
            results.append(result)

        return {
            "sent_count": len(results),
            "total_users": len(active_users),
            "message": "维护通知发送成功"
        }

    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """获取通知统计信息"""
        stats = {
            "total_notifications": 0,
            "unread_notifications": 0,
            "notifications_by_type": {},
            "notifications_by_priority": {},
            "recent_notifications": []
        }

        # 模拟统计数据
        filters = {"user_id": user_id}
        notifications = self._query_notifications_from_db(filters, limit=100)

        stats["total_notifications"] = len(notifications)
        stats["unread_notifications"] = len([n for n in notifications if not n["is_read"]])

        # 按类型统计
        type_counts = {}
        priority_counts = {}

        for notification in notifications:
            # 类型统计
            notif_type = notification["type"]
            type_counts[notif_type] = type_counts.get(notif_type, 0) + 1

            # 优先级统计
            priority = notification["priority"]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        stats["notifications_by_type"] = type_counts
        stats["notifications_by_priority"] = priority_counts
        stats["recent_notifications"] = notifications[:5]

        return stats

    def cleanup_expired_notifications(self) -> int:
        """清理过期通知"""
        expired_count = self._delete_expired_notifications()
        return expired_count

    # 私有方法（模拟数据库操作）

    def _get_user_notification_count(self, user_id: int) -> int:
        """获取用户通知数量"""
        # 模拟查询
        return 0

    def _cleanup_old_notifications(self, user_id: int) -> int:
        """清理用户旧通知"""
        # 模拟清理
        return 0

    def _save_notification_to_db(self, notification: Dict[str, Any]) -> int:
        """保存通知到数据库"""
        # 模拟保存，返回ID
        return hash(frozenset(notification.items())) % 1000000

    def _query_notifications_from_db(self, filters: Dict[str, Any], limit: int, offset: int = 0) -> List[Dict[str, Any]]:
        """从数据库查询通知"""
        # 模拟查询结果
        return []

    def _count_unread_notifications(self, user_id: int) -> int:
        """统计未读通知数量"""
        # 模拟统计
        return 0

    def _update_notification_read_status(self, notification_id: int, is_read: bool) -> bool:
        """更新通知读取状态"""
        # 模拟更新
        return True

    def _update_all_notifications_read_status(self, user_id: int) -> int:
        """更新所有通知为已读"""
        # 模拟批量更新
        return 0

    def _delete_notification_from_db(self, notification_id: int, user_id: int) -> bool:
        """删除通知"""
        # 模拟删除
        return True

    def _get_active_users(self) -> List[User]:
        """获取活跃用户"""
        # 模拟查询活跃用户
        return []

    def _delete_expired_notifications(self) -> int:
        """删除过期通知"""
        # 模拟删除
        return 0

    # 消息生成方法

    def _generate_growth_message(self, event_type: str, details: Dict[str, Any]) -> str:
        """生成成长通知消息"""
        messages = {
            "level_up": f"恭喜！您的角色等级提升到了 {details.get('new_level', 1)} 级",
            "skill_unlock": f"恭喜！解锁了新技能：{details.get('skill_name', '未知技能')}",
            "achievement": f"恭喜！获得了成就：{details.get('achievement_name', '未知成就')}",
            "milestone": f"恭喜！达到了重要里程碑：{details.get('milestone_name', '未知里程碑')}"
        }
        return messages.get(event_type, "您的角色有了新的成长！")

    def _generate_activity_title(self, activity_type: str, details: Dict[str, Any]) -> str:
        """生成活动通知标题"""
        titles = {
            "achievement": "🎉 获得新成就",
            "milestone": "🏆 达成里程碑",
            "streak": "🔥 连续使用奖励",
            "engagement": "💪 参与度提升"
        }
        return titles.get(activity_type, "活动通知")

    def _generate_activity_message(self, activity_type: str, details: Dict[str, Any]) -> str:
        """生成活动通知消息"""
        messages = {
            "achievement": f"恭喜您获得了成就：{details.get('achievement_name', '未知成就')}",
            "milestone": f"恭喜您达成了里程碑：{details.get('milestone_name', '未知里程碑')}",
            "streak": f"您已连续使用 {details.get('days', 0)} 天，继续保持！",
            "engagement": f"您的参与度提升到了 {details.get('level', 'unknown')} 等级"
        }
        return messages.get(activity_type, "您有了新的活动记录！")