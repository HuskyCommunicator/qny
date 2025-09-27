"""
智能角色推荐系统
基于用户行为分析和协同过滤算法实现个性化角色推荐
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import json
import math
from collections import defaultdict, Counter

from ..models import User, Role, ChatSession, ChatMessage, UserRole
from ..schemas.role import RoleOut


class RecommendationEngine:
    """智能推荐引擎"""

    def __init__(self, db: Session):
        self.db = db
        self.user_behavior_cache = {}
        self.role_similarity_cache = {}

    def get_user_behavior_analysis(self, user_id: int) -> Dict[str, Any]:
        """分析用户行为模式"""
        # 检查缓存 (30分钟有效期)
        if user_id in self.user_behavior_cache:
            cache_time, data = self.user_behavior_cache[user_id]
            if datetime.now() - cache_time < timedelta(minutes=30):
                return data

        # 获取用户聊天历史
        user_sessions = self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).all()

        # 分析角色使用频率
        role_usage = defaultdict(int)
        role_message_count = defaultdict(int)
        category_preference = defaultdict(int)
        tag_preference = defaultdict(int)

        total_sessions = len(user_sessions)
        total_messages = 0

        for session in user_sessions:
            if session.role_id:
                role_usage[session.role_id] += 1
                total_messages += session.message_count or 0

                # 获取角色信息
                role = self.db.query(Role).filter(Role.id == session.role_id).first()
                if role:
                    # 统计分类偏好
                    if role.category:
                        category_preference[role.category] += 1

                    # 统计标签偏好
                    if role.tags:
                        for tag in role.tags:
                            tag_preference[tag] += 1

        # 分析用户活跃度
        active_days = set()
        for session in user_sessions:
            if session.created_at:
                active_days.add(session.created_at.date())

        activity_level = len(active_days)

        # 构建用户画像
        user_profile = {
            "user_id": user_id,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "activity_level": activity_level,
            "role_usage": dict(role_usage),
            "role_message_count": dict(role_message_count),
            "category_preference": dict(category_preference),
            "tag_preference": dict(tag_preference),
            "favorite_categories": self._get_top_items(category_preference, 3),
            "favorite_tags": self._get_top_items(tag_preference, 5),
            "most_used_roles": self._get_top_items(role_usage, 3)
        }

        # 缓存结果
        self.user_behavior_cache[user_id] = (datetime.now(), user_profile)

        return user_profile

    def _get_top_items(self, data: Dict[str, int], limit: int) -> List[Tuple[str, int]]:
        """获取排名前N的项目"""
        sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:limit]

    def get_collaborative_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """基于协同过滤的推荐"""
        user_profile = self.get_user_behavior_analysis(user_id)

        # 如果用户是新用户，返回热门角色
        if user_profile["total_sessions"] == 0:
            return self.get_popular_roles(limit)

        # 获取用户常用的角色
        used_role_ids = set(user_profile["role_usage"].keys())

        # 找到相似用户
        similar_users = self._find_similar_users(user_id, user_profile)

        # 收集推荐候选
        recommendations = defaultdict(float)

        for similar_user_id, similarity_score in similar_users:
            similar_user_profile = self.get_user_behavior_analysis(similar_user_id)

            # 推荐相似用户使用过但当前用户未使用的角色
            for role_id, usage_count in similar_user_profile["role_usage"].items():
                if role_id not in used_role_ids:
                    recommendations[role_id] += similarity_score * usage_count

        # 获取推荐角色详情并归一化分数
        recommended_roles = []
        max_score = max([score for _, score in recommendations.items()]) if recommendations else 1.0

        for role_id, score in sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:limit]:
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if role:
                # 归一化分数到0-1范围
                normalized_score = min(score / max_score, 1.0)
                recommended_roles.append({
                    "role": role,
                    "score": round(normalized_score, 2),
                    "reason": "similar_users"
                })

        return recommended_roles

    def _find_similar_users(self, user_id: int, user_profile: Dict[str, Any], limit: int = 10) -> List[Tuple[int, float]]:
        """找到相似用户"""
        all_users = self.db.query(User.id).filter(User.id != user_id).all()
        similar_users = []

        for other_user in all_users:
            other_user_id = other_user[0]
            other_profile = self.get_user_behavior_analysis(other_user_id)

            # 计算用户相似度
            similarity = self._calculate_user_similarity(user_profile, other_profile)

            if similarity > 0.1:  # 相似度阈值
                similar_users.append((other_user_id, similarity))

        # 返回最相似的用户
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users[:limit]

    def _calculate_user_similarity(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> float:
        """计算用户相似度"""
        # 基于分类偏好相似度
        categories1 = set([cat for cat, _ in profile1["favorite_categories"]])
        categories2 = set([cat for cat, _ in profile2["favorite_categories"]])

        if categories1 or categories2:
            category_intersection = len(categories1.intersection(categories2))
            category_union = len(categories1.union(categories2))
            category_sim = category_intersection / category_union if category_union > 0 else 0.0
        else:
            category_sim = 0.0

        # 基于标签偏好相似度
        tags1 = set([tag for tag, _ in profile1["favorite_tags"]])
        tags2 = set([tag for tag, _ in profile2["favorite_tags"]])

        if tags1 or tags2:
            tag_intersection = len(tags1.intersection(tags2))
            tag_union = len(tags1.union(tags2))
            tag_sim = tag_intersection / tag_union if tag_union > 0 else 0.0
        else:
            tag_sim = 0.0

        # 综合相似度
        similarity = 0.5 * category_sim + 0.5 * tag_sim
        return similarity

    def get_content_based_recommendations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """基于内容的推荐"""
        user_profile = self.get_user_behavior_analysis(user_id)

        # 冷启动处理：如果用户是新用户，使用默认推荐策略
        if user_profile["total_sessions"] == 0:
            return self._get_default_recommendations(limit)

        # 获取所有角色
        all_roles = self.db.query(Role).filter(Role.is_active == True).all()
        used_role_ids = set(user_profile["role_usage"].keys())

        recommendations = []

        for role in all_roles:
            if role.id not in used_role_ids:
                # 计算角色与用户偏好的匹配度
                match_score = self._calculate_content_match_score(user_profile, role)
                if match_score > 0.1:
                    recommendations.append({
                        "role": role,
                        "score": round(match_score, 2),
                        "reason": "content_match"
                    })

        # 如果没有足够的推荐结果，补充默认推荐
        if len(recommendations) < limit:
            default_recs = self._get_default_recommendations(limit - len(recommendations))
            seen_roles = set([rec["role"].id for rec in recommendations])
            for default_rec in default_recs:
                if default_rec["role"].id not in seen_roles:
                    recommendations.append(default_rec)
                    seen_roles.add(default_rec["role"].id)

        # 返回分数最高的推荐
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]

    def _calculate_content_match_score(self, user_profile: Dict[str, Any], role: Role) -> float:
        """计算内容匹配分数"""
        score = 0.0

        # 基于分类偏好
        favorite_categories = dict(user_profile["favorite_categories"])
        if role.category and role.category in favorite_categories:
            category_total = sum(favorite_categories.values())
            if category_total > 0:
                score += 0.4 * (favorite_categories[role.category] / category_total)

        # 基于标签偏好
        favorite_tags = dict(user_profile["favorite_tags"])
        if role.tags and favorite_tags:
            tags_total = sum(favorite_tags.values())
            for tag in role.tags:
                if tag in favorite_tags and tags_total > 0:
                    score += 0.6 * (favorite_tags[tag] / tags_total)

        return min(score, 1.0)  # 限制最大分数为1.0

    def get_popular_roles(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取热门角色推荐"""
        # 统计角色使用次数
        role_stats = self.db.query(
            Role.id,
            func.count(ChatSession.id).label('usage_count')
        ).join(
            ChatSession, Role.id == ChatSession.role_id
        ).filter(
            Role.is_active == True
        ).group_by(
            Role.id
        ).all()

        # 获取热门角色
        popular_roles = []
        max_usage = max([usage_count for _, usage_count in role_stats]) if role_stats else 1
        used_role_ids = set([role_id for role_id, _ in role_stats])

        for role_id, usage_count in role_stats:
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if role and usage_count > 0:
                # 归一化分数到0-1范围
                normalized_score = min(usage_count / max_usage, 1.0)
                popular_roles.append({
                    "role": role,
                    "score": round(normalized_score, 2),
                    "reason": "popular"
                })

        # 获取没有使用数据的新角色（新角色冷启动处理）
        if len(popular_roles) < limit:
            new_roles = self.db.query(Role).filter(
                Role.is_active == True,
                Role.id.notin_(used_role_ids)
            ).all()

            # 为新角色创建推荐
            for role in new_roles:
                # 新角色给予基础分数，基于创建时间和公开状态
                new_score = 0.3  # 基础分数
                if role.is_public:
                    new_score += 0.2
                if role.created_by and role.created_by > 0:  # 有效创建者
                    new_score += 0.1

                popular_roles.append({
                    "role": role,
                    "score": round(min(new_score, 1.0), 2),
                    "reason": "new_role"
                })

        # 按分数排序
        popular_roles.sort(key=lambda x: x["score"], reverse=True)
        return popular_roles[:limit]

    def get_hybrid_recommendations(self, user_id: int, limit: int = 8) -> List[Dict[str, Any]]:
        """混合推荐算法"""
        # 获取不同算法的推荐
        collaborative_recs = self.get_collaborative_recommendations(user_id, limit // 2)
        content_recs = self.get_content_based_recommendations(user_id, limit // 2)

        # 合并推荐结果
        all_recommendations = collaborative_recs + content_recs

        # 去重并按分数排序
        seen_roles = set()
        final_recommendations = []

        for rec in all_recommendations:
            role_id = rec["role"].id
            if role_id not in seen_roles:
                seen_roles.add(role_id)
                final_recommendations.append(rec)

        # 如果推荐数量不足，补充热门角色
        if len(final_recommendations) < limit:
            popular_roles = self.get_popular_roles(limit - len(final_recommendations))
            for popular_rec in popular_roles:
                role_id = popular_rec["role"].id
                if role_id not in seen_roles:
                    final_recommendations.append(popular_rec)

        return final_recommendations[:limit]

    def track_user_interaction(self, user_id: int, role_id: int, interaction_type: str):
        """追踪用户交互行为"""
        # 这里可以添加用户行为追踪逻辑
        # 比如记录点击、聊天时长等
        pass

    def get_recommendation_explanation(self, user_id: int, role_id: int) -> Dict[str, Any]:
        """获取推荐解释"""
        user_profile = self.get_user_behavior_analysis(user_id)
        role = self.db.query(Role).filter(Role.id == role_id).first()

        if not role:
            return {"error": "Role not found"}

        explanation = {
            "role_name": role.name,
            "reasons": []
        }

        # 检查内容匹配原因
        if role.category and role.category in dict(user_profile["favorite_categories"]):
            explanation["reasons"].append(f"你对{role.category}类角色很感兴趣")

        if role.tags:
            user_tags = set([tag for tag, _ in user_profile["favorite_tags"]])
            matching_tags = set(role.tags) & user_tags
            if matching_tags:
                explanation["reasons"].append(f"你对{', '.join(matching_tags)}主题感兴趣")

        # 如果没有明显匹配，给出通用推荐理由
        if not explanation["reasons"]:
            explanation["reasons"].append("这是一个热门角色，可能适合你")

        return explanation

    def _get_default_recommendations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取新用户的默认推荐"""
        # 默认推荐策略：基于角色的描述和名称关键词匹配
        default_roles = []

        # 获取所有活跃角色
        all_roles = self.db.query(Role).filter(Role.is_active == True).all()

        # 定义默认推荐的关键词和权重
        default_keywords = {
            "编程": ["编程", "代码", "python", "javascript", "开发"],
            "教育": ["教育", "学习", "老师", "专家", "顾问"],
            "娱乐": ["娱乐", "游戏", "电影", "音乐", "聊天"],
            "心理": ["心理", "情感", "咨询", "健康", "支持"],
            "推理": ["推理", "侦探", "分析", "逻辑", "思考"]
        }

        for role in all_roles:
            score = 0.0
            role_text = (role.name + role.description).lower()

            # 计算与默认关键词的匹配度
            for category, keywords in default_keywords.items():
                for keyword in keywords:
                    if keyword in role_text:
                        score += 0.2

            # 如果角色有特定的吸引力特征，给予额外分数
            if any(word in role.description.lower() for word in ["专业", " expert", "擅长"]):
                score += 0.3

            if role.is_public:
                score += 0.2

            if score > 0.1:
                default_roles.append({
                    "role": role,
                    "score": round(min(score, 1.0), 2),
                    "reason": "default_recommendation"
                })

        # 按分数排序并返回
        default_roles.sort(key=lambda x: x["score"], reverse=True)
        return default_roles[:limit]


# 推荐服务工厂函数
def get_recommendation_engine(db: Session) -> RecommendationEngine:
    """获取推荐引擎实例"""
    return RecommendationEngine(db)