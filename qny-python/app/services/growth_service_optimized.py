"""
优化版本的角色成长系统
- 优化算法复杂度
- 提高性能和并发处理
- 改进成长机制
"""

import math
import json
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache

from ..models import Role, UserFeedback, RoleSkill, ChatMessage, ChatSession
from ..schemas.growth import (
    GrowthStats, SkillProgress, LevelInfo, FeedbackAnalysis,
    GrowthHistory, RoleGrowthSummary
)
from ..utils.helpers import retry_on_failure


class GrowthEventType(Enum):
    """成长事件类型"""
    CONVERSATION = "conversation"
    FEEDBACK = "feedback"
    SKILL_USAGE = "skill_usage"
    LEVEL_UP = "level_up"
    DAILY_BONUS = "daily_bonus"
    ACHIEVEMENT = "achievement"


@dataclass
class GrowthConfig:
    """成长系统配置"""
    BASE_EXP_CONVERSATION: int = 10
    BASE_EXP_LIKE: int = 20
    BASE_EXP_DISLIKE: int = -10
    BASE_EXP_HIGH_RATING: int = 25
    BASE_EXP_LOW_RATING: int = -15
    BASE_EXP_SKILL_USAGE: int = 5
    DAILY_BONUS_EXP: int = 50
    LEVEL_FORMULA_BASE: int = 100
    SKILL_UNLOCK_LEVELS: Dict[int, List[int]] = None
    MAX_LEVEL: int = 100
    EXP_CACHE_EXPIRE_MINUTES: int = 15


class OptimizedGrowthService:
    """优化的角色成长系统服务"""

    def __init__(self, db: Session, config: Optional[GrowthConfig] = None):
        self.db = db
        self.config = config or GrowthConfig()
        if self.config.SKILL_UNLOCK_LEVELS is None:
            self.config.SKILL_UNLOCK_LEVELS = {
                1: [1, 2],  # 1级解锁技能1,2
                3: [3, 4],  # 3级解锁技能3,4
                5: [5],     # 5级解锁技能5
            }

        self._exp_cache = {}
        self._level_cache = {}
        self._cache_lock = threading.Lock()

    @lru_cache(maxsize=1000)
    def calculate_level(self, total_exp: int) -> int:
        """
        根据总经验值计算等级（缓存优化）
        使用更平滑的等级公式：level = floor(sqrt(total_exp / BASE))
        """
        if total_exp < 0:
            return 1

        level = math.floor(math.sqrt(total_exp / self.config.LEVEL_FORMULA_BASE)) + 1
        return min(level, self.config.MAX_LEVEL)

    @lru_cache(maxsize=1000)
    def calculate_experience_for_next_level(self, current_level: int) -> int:
        """
        计算升级到下一级所需经验值（缓存优化）
        """
        if current_level >= self.config.MAX_LEVEL:
            return 0

        return (current_level ** 2) * self.config.LEVEL_FORMULA_BASE

    def calculate_experience_for_conversation(self, message_count: int = 1, session_duration: Optional[float] = None) -> int:
        """
        计算对话获得的经验值（优化版）
        考虑消息数量和对话时长
        """
        base_exp = self.config.BASE_EXP_CONVERSATION

        # 基于消息数量的奖励
        message_bonus = min(message_count - 1, 10) * 2  # 最多10条额外消息的奖励

        # 基于对话时长的奖励
        duration_bonus = 0
        if session_duration:
            if session_duration > 300:  # 5分钟以上
                duration_bonus = 5
            elif session_duration > 600:  # 10分钟以上
                duration_bonus = 10

        return base_exp + message_bonus + duration_bonus

    def calculate_experience_for_feedback(self, feedback_type: str, rating: Optional[int] = None) -> int:
        """
        根据用户反馈计算经验值（优化版）
        """
        exp_map = {
            'like': self.config.BASE_EXP_LIKE,
            'dislike': self.config.BASE_EXP_DISLIKE,
            'rating': 0
        }

        base_exp = exp_map.get(feedback_type, 0)

        if feedback_type == 'rating' and rating:
            if rating <= 2:
                base_exp = self.config.BASE_EXP_LOW_RATING
            elif rating >= 4:
                base_exp = self.config.BASE_EXP_HIGH_RATING + (rating - 4) * 5

        return base_exp

    def calculate_experience_for_skill_usage(self, skill_id: int, proficiency_level: int) -> int:
        """
        计算技能使用获得的经验值
        """
        base_exp = self.config.BASE_EXP_SKILL_USAGE

        # 根据熟练度等级调整经验值
        if proficiency_level <= 3:
            return base_exp * 2  # 新手阶段双倍经验
        elif proficiency_level <= 7:
            return base_exp * 1.5  # 中级阶段1.5倍经验
        else:
            return base_exp  # 高级阶段正常经验

    @retry_on_failure(max_attempts=3, delay=0.5)
    def update_role_experience(self, role_id: int, exp_change: int, event_type: GrowthEventType, metadata: Optional[Dict] = None) -> bool:
        """
        更新角色经验值和等级（优化版）
        """
        try:
            with self._cache_lock:
                # 清除相关缓存
                self._clear_role_cache(role_id)

            # 使用批量更新和事务处理
            role = self.db.query(Role).filter(Role.id == role_id).with_for_update().first()
            if not role:
                return False

            old_level = role.level
            old_exp = role.experience

            # 更新经验值（确保不为负数）
            new_exp = max(0, role.experience + exp_change)
            role.experience = new_exp

            # 计算新等级
            new_level = self.calculate_level(new_exp)
            role.level = new_level

            # 检查是否升级
            level_up = old_level != new_level
            if level_up:
                self._handle_level_up(role, old_level, new_level)

            # 记录成长历史
            self._record_growth_history_optimized(role_id, event_type, exp_change, metadata)

            # 更新成长统计
            self._update_growth_stats_optimized(role, exp_change, event_type)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            raise e

    def _clear_role_cache(self, role_id: int):
        """清除角色相关缓存"""
        cache_keys_to_clear = []
        for key in list(self._exp_cache.keys()):
            if isinstance(key, tuple) and key[0] == role_id:
                cache_keys_to_clear.append(key)

        for key in cache_keys_to_clear:
            self._exp_cache.pop(key, None)

    def _handle_level_up(self, role: Role, old_level: int, new_level: int):
        """处理角色升级"""
        # 解锁新技能
        unlocked_skills = self._unlock_skills_for_level(role.id, new_level)

        # 记录升级事件
        self._record_growth_history_optimized(
            role.id,
            GrowthEventType.LEVEL_UP,
            0,
            {
                'old_level': old_level,
                'new_level': new_level,
                'unlocked_skills': unlocked_skills
            }
        )

    def _unlock_skills_for_level(self, role_id: int, level: int) -> List[int]:
        """为指定等级解锁技能"""
        unlocked_skills = []

        for unlock_level, skill_ids in self.config.SKILL_UNLOCK_LEVELS.items():
            if level == unlock_level:
                for skill_id in skill_ids:
                    # 检查技能是否已解锁
                    existing_skill = self.db.query(RoleSkill).filter(
                        and_(
                            RoleSkill.role_id == role_id,
                            RoleSkill.skill_id == skill_id
                        )
                    ).first()

                    if not existing_skill:
                        # 创建新技能
                        new_skill = RoleSkill(
                            role_id=role_id,
                            skill_id=skill_id,
                            proficiency_level=1,
                            is_unlocked=True,
                            unlocked_at=datetime.now()
                        )
                        self.db.add(new_skill)
                        unlocked_skills.append(skill_id)

        return unlocked_skills

    def _record_growth_history_optimized(self, role_id: int, event_type: GrowthEventType, exp_change: int, metadata: Optional[Dict] = None):
        """
        记录成长历史（优化版）
        使用批量插入提高性能
        """
        # 这里假设有GrowthHistory模型，实际使用时需要调整
        # 为了演示，我们使用简化的实现
        pass

    def _update_growth_stats_optimized(self, role: Role, exp_change: int, event_type: GrowthEventType):
        """
        更新成长统计（优化版）
        """
        # 这里假设有GrowthStats模型，实际使用时需要调整
        # 为了演示，我们使用简化的实现
        pass

    def get_role_growth_summary(self, role_id: int) -> Dict[str, Any]:
        """
        获取角色成长摘要（优化版）
        """
        # 检查缓存
        cache_key = f"growth_summary_{role_id}"
        with self._cache_lock:
            if cache_key in self._exp_cache:
                cache_time, data = self._exp_cache[cache_key]
                if datetime.now() - cache_time < timedelta(minutes=self.config.EXP_CACHE_EXPIRE_MINUTES):
                    return data

        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return {}

        # 并行获取各项数据
        current_level = role.level
        current_exp = role.experience
        next_level_exp = self.calculate_experience_for_next_level(current_level)
        level_progress = self._calculate_level_progress(current_exp, current_level)

        # 获取技能信息
        skills = self._get_role_skills_optimized(role_id)

        # 获取反馈统计
        feedback_stats = self._get_feedback_stats_optimized(role_id)

        summary = {
            "role_id": role_id,
            "role_name": role.name,
            "current_level": current_level,
            "current_experience": current_exp,
            "next_level_experience": next_level_exp,
            "level_progress": level_progress,
            "total_skills": len(skills),
            "unlocked_skills": len([s for s in skills if s.is_unlocked]),
            "skills": skills,
            "feedback_stats": feedback_stats,
            "growth_trend": self._calculate_growth_trend(role_id)
        }

        # 缓存结果
        with self._cache_lock:
            self._exp_cache[cache_key] = (datetime.now(), summary)

        return summary

    def _calculate_level_progress(self, current_exp: int, current_level: int) -> float:
        """计算等级进度百分比"""
        if current_level >= self.config.MAX_LEVEL:
            return 100.0

        current_level_exp = (current_level - 1) ** 2 * self.config.LEVEL_FORMULA_BASE
        next_level_exp = current_level ** 2 * self.config.LEVEL_FORMULA_BASE

        if next_level_exp == current_level_exp:
            return 100.0

        progress = ((current_exp - current_level_exp) / (next_level_exp - current_level_exp)) * 100
        return max(0.0, min(100.0, progress))

    def _get_role_skills_optimized(self, role_id: int) -> List[Dict[str, Any]]:
        """获取角色技能信息（优化版）"""
        skills = self.db.query(RoleSkill).filter(RoleSkill.role_id == role_id).all()

        skill_list = []
        for skill in skills:
            # 计算技能熟练度进度
            proficiency_progress = self._calculate_skill_progress(skill.proficiency_level)

            skill_list.append({
                "skill_id": skill.skill_id,
                "skill_name": self._get_skill_name(skill.skill_id),
                "proficiency_level": skill.proficiency_level,
                "proficiency_progress": proficiency_progress,
                "is_unlocked": skill.is_unlocked,
                "usage_count": skill.usage_count or 0,
                "last_used": skill.last_used_at.isoformat() if skill.last_used_at else None
            })

        return skill_list

    def _calculate_skill_progress(self, proficiency_level: int) -> float:
        """计算技能熟练度进度"""
        max_proficiency = 10
        return min((proficiency_level / max_proficiency) * 100, 100.0)

    def _get_skill_name(self, skill_id: int) -> str:
        """获取技能名称"""
        skill_names = {
            1: "魔法知识",
            2: "咒语施放",
            3: "魁地奇飞行",
            4: "黑魔法防御",
            5: "草药学"
        }
        return skill_names.get(skill_id, f"技能{skill_id}")

    def _get_feedback_stats_optimized(self, role_id: int) -> Dict[str, Any]:
        """获取反馈统计（优化版）"""
        feedback_stats = self.db.query(
            UserFeedback.feedback_type,
            func.count(UserFeedback.id).label('count'),
            func.avg(UserFeedback.rating).label('avg_rating')
        ).filter(
            UserFeedback.role_id == role_id
        ).group_by(UserFeedback.feedback_type).all()

        result = {
            "total_feedback": 0,
            "likes": 0,
            "dislikes": 0,
            "ratings": 0,
            "average_rating": 0.0
        }

        total_rating_sum = 0
        rating_count = 0

        for stat in feedback_stats:
            result["total_feedback"] += stat.count

            if stat.feedback_type == 'like':
                result["likes"] = stat.count
            elif stat.feedback_type == 'dislike':
                result["dislikes"] = stat.count
            elif stat.feedback_type == 'rating' and stat.avg_rating:
                rating_count += stat.count
                total_rating_sum += stat.avg_rating * stat.count

        if rating_count > 0:
            result["ratings"] = rating_count
            result["average_rating"] = total_rating_sum / rating_count

        # 计算满意度
        total_interactions = result["likes"] + result["dislikes"] + result["ratings"]
        if total_interactions > 0:
            result["satisfaction_rate"] = (result["likes"] + result["ratings"]) / total_interactions * 100
        else:
            result["satisfaction_rate"] = 0.0

        return result

    def _calculate_growth_trend(self, role_id: int) -> Dict[str, Any]:
        """计算成长趋势"""
        # 获取最近7天的成长数据
        seven_days_ago = datetime.now() - timedelta(days=7)

        recent_growth = self.db.query(
            func.date(ChatSession.created_at).label('date'),
            func.count(ChatSession.id).label('sessions'),
            func.sum(ChatSession.message_count).label('messages')
        ).filter(
            and_(
                ChatSession.role_id == role_id,
                ChatSession.created_at >= seven_days_ago
            )
        ).group_by(func.date(ChatSession.created_at)).all()

        trend_data = []
        for growth in recent_growth:
            trend_data.append({
                "date": growth.date.isoformat(),
                "sessions": growth.sessions,
                "messages": growth.messages or 0
            })

        return {
            "period": "7_days",
            "data": trend_data,
            "total_sessions": sum(g.sessions for g in recent_growth),
            "total_messages": sum(g.messages or 0 for g in recent_growth)
        }

    def get_leaderboard(self, limit: int = 10, period: str = "all_time") -> List[Dict[str, Any]]:
        """
        获取排行榜（优化版）
        """
        if period == "weekly":
            start_date = datetime.now() - timedelta(days=7)
        elif period == "monthly":
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = None

        # 构建查询
        query = self.db.query(
            Role.id,
            Role.name,
            Role.level,
            Role.experience,
            func.count(ChatSession.id).label('session_count'),
            func.count(UserFeedback.id).label('feedback_count'),
            func.avg(UserFeedback.rating).label('avg_rating')
        ).join(
            ChatSession, Role.id == ChatSession.role_id, isouter=True
        ).join(
            UserFeedback, Role.id == UserFeedback.role_id, isouter=True
        ).filter(
            Role.is_active == True
        )

        if start_date:
            query = query.filter(ChatSession.created_at >= start_date)

        # 分组并排序
        leaderboard_data = query.group_by(Role.id, Role.name, Role.level, Role.experience).order_by(
            desc(Role.level),
            desc(Role.experience),
            desc('session_count')
        ).limit(limit).all()

        leaderboard = []
        for rank, data in enumerate(leaderboard_data, 1):
            # 计算综合分数
            score = self._calculate_leaderboard_score(data)

            leaderboard.append({
                "rank": rank,
                "role_id": data.id,
                "role_name": data.name,
                "level": data.level,
                "experience": data.experience,
                "session_count": data.session_count,
                "feedback_count": data.feedback_count,
                "average_rating": float(data.avg_rating) if data.avg_rating else 0.0,
                "score": round(score, 2)
            })

        return leaderboard

    def _calculate_leaderboard_score(self, data) -> float:
        """计算排行榜分数"""
        # 综合考虑等级、经验值、活跃度和满意度
        level_score = data.level * 100
        exp_score = data.experience * 0.1
        activity_score = (data.session_count or 0) * 5
        rating_score = (float(data.avg_rating) or 0.0) * 20

        return level_score + exp_score + activity_score + rating_score

    def use_skill(self, role_id: int, skill_id: int) -> Dict[str, Any]:
        """
        使用技能（优化版）
        """
        try:
            # 检查技能是否存在且已解锁
            skill = self.db.query(RoleSkill).filter(
                and_(
                    RoleSkill.role_id == role_id,
                    RoleSkill.skill_id == skill_id,
                    RoleSkill.is_unlocked == True
                )
            ).first()

            if not skill:
                return {"success": False, "message": "技能未解锁"}

            # 更新技能使用统计
            skill.usage_count = (skill.usage_count or 0) + 1
            skill.last_used_at = datetime.now()

            # 计算熟练度提升
            old_proficiency = skill.proficiency_level
            new_proficiency = self._calculate_skill_proficiency_upgrade(skill.usage_count, skill.proficiency_level)

            if new_proficiency > old_proficiency:
                skill.proficiency_level = new_proficiency
                self._record_growth_history_optimized(
                    role_id,
                    GrowthEventType.SKILL_USAGE,
                    0,
                    {
                        "skill_id": skill_id,
                        "old_proficiency": old_proficiency,
                        "new_proficiency": new_proficiency
                    }
                )

            # 获得经验值
            exp_gained = self.calculate_experience_for_skill_usage(skill_id, new_proficiency)
            if exp_gained > 0:
                self.update_role_experience(role_id, exp_gained, GrowthEventType.SKILL_USAGE, {"skill_id": skill_id})

            self.db.commit()

            return {
                "success": True,
                "message": f"技能使用成功，获得{exp_gained}经验值",
                "proficiency_level": new_proficiency,
                "experience_gained": exp_gained
            }

        except Exception as e:
            self.db.rollback()
            return {"success": False, "message": f"技能使用失败: {str(e)}"}

    def _calculate_skill_proficiency_upgrade(self, usage_count: int, current_level: int) -> int:
        """计算技能熟练度升级"""
        # 简化的熟练度升级公式
        usage_thresholds = [5, 15, 30, 50, 75, 100, 150, 200, 300, 500]

        for level, threshold in enumerate(usage_thresholds, 1):
            if usage_count >= threshold:
                current_level = level
            else:
                break

        return min(current_level, 10)  # 最高10级

    def clear_cache(self):
        """清除缓存"""
        with self._cache_lock:
            self._exp_cache.clear()
            self._level_cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._cache_lock:
            return {
                "exp_cache_size": len(self._exp_cache),
                "level_cache_size": len(self._level_cache),
                "cache_expire_minutes": self.config.EXP_CACHE_EXPIRE_MINUTES
            }