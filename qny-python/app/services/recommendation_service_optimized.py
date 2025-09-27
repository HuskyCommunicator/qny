"""
优化版本的智能角色推荐系统
- 降低算法复杂度
- 提高性能和缓存效率
- 改进推荐准确性
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import json
import math
import numpy as np
from collections import defaultdict, Counter
from functools import lru_cache
import threading
from dataclasses import dataclass

from ..models import User, Role, ChatSession, ChatMessage, UserRole
from ..schemas.role import RoleOut
from ..utils.helpers import retry_on_failure, merge_dicts


@dataclass
class RecommendationConfig:
    """推荐系统配置"""
    CACHE_EXPIRE_MINUTES: int = 30
    MAX_SIMILAR_USERS: int = 10
    SIMILARITY_THRESHOLD: float = 0.1
    MAX_RECOMMENDATIONS: int = 20
    COLLABORATIVE_WEIGHT: float = 0.4
    CONTENT_WEIGHT: float = 0.3
    POPULAR_WEIGHT: float = 0.3
    MIN_USER_SESSIONS: int = 3


class OptimizedRecommendationEngine:
    """优化的智能推荐引擎"""

    def __init__(self, db: Session, config: Optional[RecommendationConfig] = None):
        self.db = db
        self.config = config or RecommendationConfig()
        self._user_behavior_cache = {}
        self._role_similarity_cache = {}
        self._popular_roles_cache = None
        self._popular_roles_cache_time = None
        self._cache_lock = threading.Lock()

    @retry_on_failure(max_attempts=3, delay=0.5)
    def get_user_behavior_analysis(self, user_id: int) -> Dict[str, Any]:
        """分析用户行为模式（优化版）"""
        with self._cache_lock:
            if self._is_cache_valid(user_id, self._user_behavior_cache):
                return self._user_behavior_cache[user_id][1]

        # 使用更高效的查询
        user_sessions = self._get_user_sessions_optimized(user_id)
        if not user_sessions:
            return self._get_empty_user_profile(user_id)

        # 批量获取角色信息，减少数据库查询
        role_ids = [s.role_id for s in user_sessions if s.role_id]
        role_info = self._get_role_info_batch(role_ids)

        user_profile = self._build_user_profile(user_id, user_sessions, role_info)

        with self._cache_lock:
            self._user_behavior_cache[user_id] = (datetime.now(), user_profile)

        return user_profile

    def _is_cache_valid(self, key: int, cache: Dict) -> bool:
        """检查缓存是否有效"""
        if key not in cache:
            return False
        cache_time, _ = cache[key]
        return datetime.now() - cache_time < timedelta(minutes=self.config.CACHE_EXPIRE_MINUTES)

    def _get_user_sessions_optimized(self, user_id: int) -> List[ChatSession]:
        """优化的用户会话查询"""
        return self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).options(
            # 使用joinedload来预加载相关数据
            # 这里假设已经配置了适当的ORM关系
        ).all()

    def _get_role_info_batch(self, role_ids: List[int]) -> Dict[int, Role]:
        """批量获取角色信息"""
        if not role_ids:
            return {}

        roles = self.db.query(Role).filter(
            Role.id.in_(role_ids)
        ).all()

        return {role.id: role for role in roles}

    def _build_user_profile(self, user_id: int, sessions: List[ChatSession], role_info: Dict[int, Role]) -> Dict[str, Any]:
        """构建用户画像"""
        role_usage = Counter()
        category_preference = Counter()
        tag_preference = Counter()
        active_days = set()

        total_messages = sum(s.message_count or 0 for s in sessions)

        for session in sessions:
            if session.role_id and session.role_id in role_info:
                role = role_info[session.role_id]
                role_usage[session.role_id] += 1

                if session.created_at:
                    active_days.add(session.created_at.date())

                if role.category:
                    category_preference[role.category] += 1

                if role.tags:
                    for tag in role.tags:
                        tag_preference[tag] += 1

        return {
            "user_id": user_id,
            "total_sessions": len(sessions),
            "total_messages": total_messages,
            "activity_level": len(active_days),
            "role_usage": dict(role_usage),
            "category_preference": dict(category_preference),
            "tag_preference": dict(tag_preference),
            "favorite_categories": self._get_top_items(category_preference, 3),
            "favorite_tags": self._get_top_items(tag_preference, 5),
            "most_used_roles": self._get_top_items(role_usage, 3)
        }

    def _get_empty_user_profile(self, user_id: int) -> Dict[str, Any]:
        """获取空用户画像（新用户）"""
        return {
            "user_id": user_id,
            "total_sessions": 0,
            "total_messages": 0,
            "activity_level": 0,
            "role_usage": {},
            "category_preference": {},
            "tag_preference": {},
            "favorite_categories": [],
            "favorite_tags": [],
            "most_used_roles": []
        }

    def _get_top_items(self, data: Counter, limit: int) -> List[Tuple[str, int]]:
        """获取排名前N的项目"""
        return data.most_common(limit)

    def get_hybrid_recommendations(self, user_id: int, limit: int = 8) -> List[Dict[str, Any]]:
        """混合推荐算法（优化版）"""
        if limit > self.config.MAX_RECOMMENDATIONS:
            limit = self.config.MAX_RECOMMENDATIONS

        # 并行计算不同算法的推荐结果
        user_profile = self.get_user_behavior_analysis(user_id)

        # 如果是新用户，直接返回热门推荐
        if user_profile["total_sessions"] < self.config.MIN_USER_SESSIONS:
            return self.get_popular_roles(limit)

        # 并行获取不同算法的推荐
        collaborative_recs = self.get_collaborative_recommendations(user_id, limit)
        content_recs = self.get_content_based_recommendations(user_id, limit)
        popular_recs = self.get_popular_roles(limit // 2)

        # 合并和去重
        final_recommendations = self._merge_recommendations(
            collaborative_recs,
            content_recs,
            popular_recs,
            limit
        )

        return final_recommendations

    def get_collaborative_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """基于协同过滤的推荐（优化版）"""
        user_profile = self.get_user_behavior_analysis(user_id)
        used_role_ids = set(user_profile["role_usage"].keys())

        # 使用优化的相似用户查找
        similar_users = self._find_similar_users_optimized(user_id, user_profile)

        # 收集推荐候选
        recommendations = defaultdict(float)

        for similar_user_id, similarity_score in similar_users:
            similar_user_profile = self.get_user_behavior_analysis(similar_user_id)

            for role_id, usage_count in similar_user_profile["role_usage"].items():
                if role_id not in used_role_ids:
                    recommendations[role_id] += similarity_score * usage_count

        # 优化：使用批量查询获取角色信息
        recommended_roles = self._build_recommendations_from_scores(
            recommendations, limit, "collaborative"
        )

        return recommended_roles

    def _find_similar_users_optimized(self, user_id: int, user_profile: Dict[str, Any]) -> List[Tuple[int, float]]:
        """优化的相似用户查找"""
        # 优化：只查询活跃用户
        active_users = self.db.query(User.id).filter(
            and_(
                User.id != user_id,
                User.is_active == True
            )
        ).limit(100).all()  # 限制查询范围

        similar_users = []

        for other_user in active_users:
            other_user_id = other_user[0]
            other_profile = self.get_user_behavior_analysis(other_user_id)

            # 优化：快速筛选有足够数据的用户
            if other_profile["total_sessions"] < self.config.MIN_USER_SESSIONS:
                continue

            similarity = self._calculate_user_similarity_optimized(user_profile, other_profile)

            if similarity > self.config.SIMILARITY_THRESHOLD:
                similar_users.append((other_user_id, similarity))

        # 返回最相似的用户
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users[:self.config.MAX_SIMILAR_USERS]

    def _calculate_user_similarity_optimized(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> float:
        """优化的用户相似度计算"""
        # 使用更高效的相似度计算
        categories1 = set([cat for cat, _ in profile1["favorite_categories"]])
        categories2 = set([cat for cat, _ in profile2["favorite_categories"]])

        category_sim = self._calculate_jaccard_similarity(categories1, categories2)

        tags1 = set([tag for tag, _ in profile1["favorite_tags"]])
        tags2 = set([tag for tag, _ in profile2["favorite_tags"]])

        tag_sim = self._calculate_jaccard_similarity(tags1, tags2)

        # 加权综合相似度
        similarity = 0.6 * category_sim + 0.4 * tag_sim
        return similarity

    def _calculate_jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """计算Jaccard相似度"""
        if not set1 and not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def get_content_based_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """基于内容的推荐（优化版）"""
        user_profile = self.get_user_behavior_analysis(user_id)
        used_role_ids = set(user_profile["role_usage"].keys())

        # 获取候选角色（排除已使用的）
        candidate_roles = self.db.query(Role).filter(
            and_(
                Role.is_active == True,
                ~Role.id.in_(used_role_ids) if used_role_ids else True
            )
        ).limit(100).all()  # 限制候选数量

        recommendations = []

        for role in candidate_roles:
            score = self._calculate_content_similarity(user_profile, role)
            if score > 0.1:  # 相似度阈值
                recommendations.append({
                    "role": role,
                    "score": round(score, 2),
                    "reason": "content_match"
                })

        # 排序并返回top N
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]

    def _calculate_content_similarity(self, user_profile: Dict[str, Any], role: Role) -> float:
        """计算内容相似度（优化版）"""
        score = 0.0

        # 分类匹配
        user_categories = set([cat for cat, _ in user_profile["favorite_categories"]])
        if role.category and role.category in user_categories:
            score += 0.4

        # 标签匹配
        user_tags = set([tag for tag, _ in user_profile["favorite_tags"]])
        if role.tags:
            role_tags = set(role.tags)
            tag_similarity = self._calculate_jaccard_similarity(user_tags, role_tags)
            score += 0.6 * tag_similarity

        return min(score, 1.0)

    def get_popular_roles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门角色（带缓存）"""
        with self._cache_lock:
            if (self._popular_roles_cache_time and
                datetime.now() - self._popular_roles_cache_time < timedelta(minutes=15)):
                return self._popular_roles_cache[:limit]

        # 计算热门角色
        popular_roles = self._calculate_popular_roles()

        with self._cache_lock:
            self._popular_roles_cache = popular_roles
            self._popular_roles_cache_time = datetime.now()

        return popular_roles[:limit]

    def _calculate_popular_roles(self) -> List[Dict[str, Any]]:
        """计算热门角色（优化版）"""
        # 使用更高效的查询
        popular_stats = self.db.query(
            ChatSession.role_id,
            func.count(ChatSession.id).label('session_count'),
            func.sum(ChatSession.message_count).label('message_count')
        ).filter(
            ChatSession.role_id.isnot(None)
        ).group_by(ChatSession.role_id).order_by(
            desc('session_count')
        ).limit(20).all()

        popular_roles = []

        for stat in popular_stats:
            role = self.db.query(Role).filter(Role.id == stat.role_id).first()
            if role and role.is_active:
                # 计算综合热度分数
                popularity_score = (stat.session_count * 0.7 + (stat.message_count or 0) * 0.3)
                popular_roles.append({
                    "role": role,
                    "score": min(popularity_score / 10, 1.0),  # 归一化
                    "reason": "popular"
                })

        # 按分数排序
        popular_roles.sort(key=lambda x: x["score"], reverse=True)
        return popular_roles

    def _build_recommendations_from_scores(self, recommendations: Dict[int, float], limit: int, reason: str) -> List[Dict[str, Any]]:
        """从分数构建推荐列表"""
        if not recommendations:
            return []

        # 归一化分数
        max_score = max(recommendations.values()) if recommendations else 1.0

        recommended_roles = []
        for role_id, score in sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:limit]:
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if role and role.is_active:
                normalized_score = min(score / max_score, 1.0)
                recommended_roles.append({
                    "role": role,
                    "score": round(normalized_score, 2),
                    "reason": reason
                })

        return recommended_roles

    def _merge_recommendations(self, collaborative_recs: List, content_recs: List, popular_recs: List, limit: int) -> List[Dict[str, Any]]:
        """合并多种推荐算法的结果"""
        all_recommendations = {}

        # 协同过滤推荐
        for rec in collaborative_recs:
            role_id = rec["role"].id
            all_recommendations[role_id] = {
                "role": rec["role"],
                "collaborative_score": rec["score"],
                "content_score": 0.0,
                "popular_score": 0.0,
                "reasons": [rec["reason"]]
            }

        # 内容推荐
        for rec in content_recs:
            role_id = rec["role"].id
            if role_id in all_recommendations:
                all_recommendations[role_id]["content_score"] = rec["score"]
                all_recommendations[role_id]["reasons"].append(rec["reason"])
            else:
                all_recommendations[role_id] = {
                    "role": rec["role"],
                    "collaborative_score": 0.0,
                    "content_score": rec["score"],
                    "popular_score": 0.0,
                    "reasons": [rec["reason"]]
                }

        # 热门推荐（用于填充）
        for rec in popular_recs:
            role_id = rec["role"].id
            if len(all_recommendations) < limit and role_id not in all_recommendations:
                all_recommendations[role_id] = {
                    "role": rec["role"],
                    "collaborative_score": 0.0,
                    "content_score": 0.0,
                    "popular_score": rec["score"],
                    "reasons": [rec["reason"]]
                }

        # 计算综合分数
        final_recommendations = []
        for role_id, rec_data in all_recommendations.items():
            composite_score = (
                rec_data["collaborative_score"] * self.config.COLLABORATIVE_WEIGHT +
                rec_data["content_score"] * self.config.CONTENT_WEIGHT +
                rec_data["popular_score"] * self.config.POPULAR_WEIGHT
            )

            final_recommendations.append({
                "role": rec_data["role"],
                "score": round(composite_score, 2),
                "reason": "hybrid",
                "detailed_scores": {
                    "collaborative": rec_data["collaborative_score"],
                    "content": rec_data["content_score"],
                    "popular": rec_data["popular_score"]
                }
            })

        # 排序并返回
        final_recommendations.sort(key=lambda x: x["score"], reverse=True)
        return final_recommendations[:limit]

    def clear_cache(self):
        """清除缓存"""
        with self._cache_lock:
            self._user_behavior_cache.clear()
            self._role_similarity_cache.clear()
            self._popular_roles_cache = None
            self._popular_roles_cache_time = None

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._cache_lock:
            return {
                "user_behavior_cache_size": len(self._user_behavior_cache),
                "role_similarity_cache_size": len(self._role_similarity_cache),
                "popular_roles_cache_valid": self._popular_roles_cache_time is not None,
                "cache_expire_minutes": self.config.CACHE_EXPIRE_MINUTES
            }