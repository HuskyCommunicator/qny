"""
成长系统服务层
实现角色成长算法、经验值计算、等级提升等核心逻辑
"""

import math
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..models import Role, UserFeedback, RoleSkill, ChatMessage, ChatSession
from ..schemas.growth import (
    GrowthStats, SkillProgress, LevelInfo, FeedbackAnalysis,
    GrowthHistory, RoleGrowthSummary
)


class GrowthService:
    """角色成长系统服务"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_experience_for_conversation(self, base_exp: int = 10) -> int:
        """
        计算单次对话获得的经验值
        """
        return base_exp

    def calculate_experience_for_feedback(self, feedback_type: str, rating: Optional[int] = None) -> int:
        """
        根据用户反馈计算经验值
        """
        exp_map = {
            'like': 20,
            'dislike': -10,
            'rating': 0  # 评分单独计算
        }

        base_exp = exp_map.get(feedback_type, 0)

        if feedback_type == 'rating' and rating:
            # 评分经验值：1-2星扣分，3星不加不减，4-5星加分
            if rating <= 2:
                base_exp = -15
            elif rating >= 4:
                base_exp = 25 + (rating - 4) * 5

        return base_exp

    def calculate_level(self, total_exp: int) -> int:
        """
        根据总经验值计算等级
        等级公式：level = floor(sqrt(total_exp / 100)) + 1
        """
        return math.floor(math.sqrt(total_exp / 100)) + 1

    def calculate_experience_for_next_level(self, current_level: int) -> int:
        """
        计算升级到下一级所需经验值
        """
        return (current_level ** 2) * 100

    def update_role_experience(self, role_id: int, exp_change: int, reason: str = "") -> bool:
        """
        更新角色经验值和等级
        """
        try:
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return False

            old_level = role.level
            old_exp = role.experience

            # 更新经验值
            role.experience = max(0, role.experience + exp_change)

            # 计算新等级
            role.level = self.calculate_level(role.experience)

            # 记录成长历史
            if old_level != role.level:
                self._record_growth_history(
                    role_id, 'level_up',
                    f"等级从 {old_level} 提升到 {role.level}",
                    {'old_level': old_level, 'new_level': role.level}
                )

            # 更新成长统计
            self._update_growth_stats(role, exp_change, reason)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            return False

    def record_conversation(self, role_id: int, user_id: int, session_id: str) -> bool:
        """
        记录对话并计算成长
        """
        try:
            # 计算经验值
            exp_gain = self.calculate_experience_for_conversation()

            # 更新角色数据
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if role:
                role.total_conversations += 1
                self.update_role_experience(role_id, exp_gain, "conversation")

            # 更新用户角色使用次数
            from ..models import UserRole
            user_role = self.db.query(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id
            ).first()
            if user_role:
                user_role.usage_count += 1
                user_role.last_used_at = datetime.utcnow()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            return False

    def record_feedback(self, user_id: int, role_id: int, message_id: Optional[int],
                       feedback_type: str, rating: Optional[int] = None,
                       feedback_reason: Optional[str] = None,
                       comment: Optional[str] = None) -> bool:
        """
        记录用户反馈并计算成长
        """
        try:
            # 计算经验值变化
            exp_change = self.calculate_experience_for_feedback(feedback_type, rating)

            # 创建反馈记录
            feedback = UserFeedback(
                user_id=user_id,
                role_id=role_id,
                message_id=message_id,
                feedback_type=feedback_type,
                rating=rating,
                feedback_reason=feedback_reason,
                comment=comment
            )
            self.db.add(feedback)

            # 更新角色反馈统计
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if role:
                if feedback_type == 'like' or (rating and rating >= 4):
                    role.positive_feedback += 1
                elif feedback_type == 'dislike' or (rating and rating <= 2):
                    role.negative_feedback += 1

                # 更新经验值
                self.update_role_experience(role_id, exp_change, f"feedback_{feedback_type}")

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            return False

    def get_role_growth_summary(self, role_id: int) -> Optional[RoleGrowthSummary]:
        """
        获取角色成长摘要
        """
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return None

        # 计算下一级所需经验值
        next_level_exp = self.calculate_experience_for_next_level(role.level)
        current_level_exp = ((role.level - 1) ** 2) * 100
        exp_progress = role.experience - current_level_exp
        exp_needed = next_level_exp - current_level_exp
        progress_percentage = (exp_progress / exp_needed * 100) if exp_needed > 0 else 0

        # 获取技能数据
        skills = self.db.query(RoleSkill).filter(
            RoleSkill.role_id == role_id
        ).order_by(desc(RoleSkill.proficiency_level)).all()

        skill_progress = []
        for skill in skills:
            skill_progress.append(SkillProgress(
                skill_name=skill.skill_name,
                skill_description=skill.skill_description,
                proficiency_level=skill.proficiency_level,
                is_unlocked=skill.is_unlocked,
                unlock_level=skill.unlock_level,
                usage_count=skill.usage_count
            ))

        return RoleGrowthSummary(
            role_id=role.id,
            role_name=role.name,
            level=role.level,
            experience=role.experience,
            next_level_exp=next_level_exp,
            exp_progress=exp_progress,
            exp_needed=exp_needed,
            progress_percentage=progress_percentage,
            total_conversations=role.total_conversations,
            positive_feedback=role.positive_feedback,
            negative_feedback=role.negative_feedback,
            skills=skill_progress,
            satisfaction_rate=self._calculate_satisfaction_rate(role),
            growth_rate=self._calculate_growth_rate(role)
        )

    def get_user_feedback_analysis(self, user_id: int, role_id: Optional[int] = None) -> FeedbackAnalysis:
        """
        获取用户反馈分析
        """
        query = self.db.query(UserFeedback).filter(UserFeedback.user_id == user_id)

        if role_id:
            query = query.filter(UserFeedback.role_id == role_id)

        feedbacks = query.all()

        total_feedbacks = len(feedbacks)
        if total_feedbacks == 0:
            return FeedbackAnalysis(
                total_feedbacks=0,
                satisfaction_rate=0.0,
                feedback_distribution={},
                common_reasons=[],
                trend_analysis="暂无数据"
            )

        # 统计反馈分布
        feedback_distribution = {'like': 0, 'dislike': 0, 'rating': 0}
        satisfaction_score = 0

        for feedback in feedbacks:
            feedback_distribution[feedback.feedback_type] += 1

            if feedback.feedback_type == 'like':
                satisfaction_score += 5
            elif feedback.feedback_type == 'dislike':
                satisfaction_score += 1
            elif feedback.rating:
                satisfaction_score += feedback.rating

        # 计算满意度
        satisfaction_rate = (satisfaction_score / (total_feedbacks * 5)) * 100

        # 分析常见原因
        reason_counts = {}
        for feedback in feedbacks:
            if feedback.feedback_reason:
                reason_counts[feedback.feedback_reason] = reason_counts.get(feedback.feedback_reason, 0) + 1

        common_reasons = sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        common_reasons = [reason for reason, count in common_reasons]

        # 趋势分析（简化版）
        trend_analysis = "反馈趋势稳定" if satisfaction_rate > 70 else "需要改进用户体验"

        return FeedbackAnalysis(
            total_feedbacks=total_feedbacks,
            satisfaction_rate=satisfaction_rate,
            feedback_distribution=feedback_distribution,
            common_reasons=common_reasons,
            trend_analysis=trend_analysis
        )

    def initialize_role_skills(self, role_id: int, role_name: str) -> bool:
        """
        为角色初始化技能数据
        """
        try:
            # 根据角色名称预设技能
            skill_templates = self._get_skill_templates_for_role(role_name)

            for i, skill_template in enumerate(skill_templates):
                skill = RoleSkill(
                    role_id=role_id,
                    skill_name=skill_template['name'],
                    skill_description=skill_template['description'],
                    skill_category=skill_template['category'],
                    proficiency_level=0,
                    is_unlocked=i < 2,  # 前两个技能默认解锁
                    unlock_level=skill_template.get('unlock_level', 1),
                    skill_metadata=skill_template.get('metadata', {})
                )
                self.db.add(skill)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            return False

    def update_skill_proficiency(self, role_id: int, skill_name: str, usage_increment: int = 1) -> bool:
        """
        更新技能熟练度
        """
        try:
            skill = self.db.query(RoleSkill).filter(
                RoleSkill.role_id == role_id,
                RoleSkill.skill_name == skill_name
            ).first()

            if not skill:
                return False

            # 增加使用次数
            skill.usage_count += usage_increment

            # 计算熟练度增长（基于使用次数，但有上限）
            usage_factor = min(skill.usage_count * 2, 80)  # 使用因子最多80分
            level_factor = min(skill.proficiency_level, 20)  # 等级因子最多20分

            new_proficiency = min(100, usage_factor + level_factor)
            skill.proficiency_level = new_proficiency

            # 检查是否应该解锁新技能
            self._check_and_unlock_skills(role_id)

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            return False

    def _record_growth_history(self, role_id: int, event_type: str, description: str, metadata: dict):
        """记录成长历史"""
        # 这里可以添加一个GrowthHistory模型来记录历史
        # 目前简化处理，直接更新角色的growth_stats字段
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if role and role.growth_stats:
            stats = role.growth_stats
            if 'history' not in stats:
                stats['history'] = []

            stats['history'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'description': description,
                'metadata': metadata
            })

            # 保持历史记录在最近100条
            if len(stats['history']) > 100:
                stats['history'] = stats['history'][-100:]

            role.growth_stats = stats

    def _update_growth_stats(self, role: Role, exp_change: int, reason: str):
        """更新成长统计数据"""
        if not role.growth_stats:
            role.growth_stats = {}

        stats = role.growth_stats

        # 更新总经验值变化
        if 'total_exp_gained' not in stats:
            stats['total_exp_gained'] = 0
        if exp_change > 0:
            stats['total_exp_gained'] += exp_change

        # 更新原因统计
        if 'reason_stats' not in stats:
            stats['reason_stats'] = {}
        if reason not in stats['reason_stats']:
            stats['reason_stats'][reason] = 0
        stats['reason_stats'][reason] += 1

        # 更新最后更新时间
        stats['last_updated'] = datetime.utcnow().isoformat()

        role.growth_stats = stats

    def _calculate_satisfaction_rate(self, role: Role) -> float:
        """计算角色满意度"""
        total_feedbacks = role.positive_feedback + role.negative_feedback
        if total_feedbacks == 0:
            return 75.0  # 默认满意度

        return (role.positive_feedback / total_feedbacks) * 100

    def _calculate_growth_rate(self, role: Role) -> float:
        """计算成长率"""
        if role.total_conversations == 0:
            return 0.0

        # 简单的成长率计算：经验值 / 对话次数
        return role.experience / max(role.total_conversations, 1)

    def _check_and_unlock_skills(self, role_id: int):
        """检查并解锁新技能"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            return

        # 查找未解锁的技能
        locked_skills = self.db.query(RoleSkill).filter(
            RoleSkill.role_id == role_id,
            RoleSkill.is_unlocked == False
        ).all()

        for skill in locked_skills:
            if role.level >= skill.unlock_level:
                skill.is_unlocked = True
                self._record_growth_history(
                    role_id, 'skill_unlock',
                    f"解锁技能：{skill.skill_name}",
                    {'skill_name': skill.skill_name, 'unlock_level': skill.unlock_level}
                )

    def _get_skill_templates_for_role(self, role_name: str) -> List[dict]:
        """根据角色名称获取技能模板"""
        templates = {
            '哈利波特': [
                {'name': '魔法知识', 'description': '掌握丰富的魔法世界知识', 'category': '专业知识', 'unlock_level': 1},
                {'name': '咒语施放', 'description': '能够施放各种魔法咒语', 'category': '实践技能', 'unlock_level': 1},
                {'name': '魁地奇飞行', 'description': '精通魁地奇飞行技巧', 'category': '运动技能', 'unlock_level': 3},
                {'name': '黑魔法防御', 'description': '具备强大的黑魔法防御能力', 'category': '战斗技能', 'unlock_level': 5},
                {'name': '草药学', 'description': '了解各种魔法植物的特性', 'category': '专业知识', 'unlock_level': 7}
            ],
            '苏格拉底': [
                {'name': '辩证思维', 'description': '运用苏格拉底式提问法', 'category': '思维技能', 'unlock_level': 1},
                {'name': '哲学知识', 'description': '掌握古希腊哲学思想', 'category': '专业知识', 'unlock_level': 1},
                {'name': '逻辑推理', 'description': '强大的逻辑分析能力', 'category': '思维技能', 'unlock_level': 3},
                {'name': '教育方法', 'description': '独特的启发式教学方法', 'category': '教学技能', 'unlock_level': 5},
                {'name': '伦理思考', 'description': '深入的伦理道德思考能力', 'category': '思维技能', 'unlock_level': 7}
            ],
            '心理咨询师': [
                {'name': '情感理解', 'description': '深刻理解他人情感', 'category': '沟通技能', 'unlock_level': 1},
                {'name': '心理分析', 'description': '专业的心理分析能力', 'category': '专业技能', 'unlock_level': 1},
                {'name': '倾听技巧', 'description': '优秀的倾听和共情能力', 'category': '沟通技能', 'unlock_level': 3},
                {'name': '危机干预', 'description': '处理心理危机的能力', 'category': '专业技能', 'unlock_level': 5},
                {'name': '治疗方案', 'description': '制定个性化治疗方案', 'category': '专业技能', 'unlock_level': 7}
            ],
            'Python编程助手': [
                {'name': 'Python语法', 'description': '精通Python语法规范', 'category': '编程技能', 'unlock_level': 1},
                {'name': '算法设计', 'description': '能够设计高效算法', 'category': '编程技能', 'unlock_level': 1},
                {'name': '调试技巧', 'description': '快速定位和修复bug', 'category': '调试技能', 'unlock_level': 3},
                {'name': '性能优化', 'description': '代码性能优化能力', 'category': '优化技能', 'unlock_level': 5},
                {'name': '架构设计', 'description': '软件架构设计能力', 'category': '设计技能', 'unlock_level': 7}
            ],
            '前端开发顾问': [
                {'name': 'HTML/CSS', 'description': '精通前端标记和样式', 'category': '前端技能', 'unlock_level': 1},
                {'name': 'JavaScript', 'description': '熟练掌握JavaScript', 'category': '编程技能', 'unlock_level': 1},
                {'name': '框架应用', 'description': '熟练使用主流前端框架', 'category': '框架技能', 'unlock_level': 3},
                {'name': '响应式设计', 'description': '响应式网页设计能力', 'category': '设计技能', 'unlock_level': 5},
                {'name': '性能优化', 'description': '前端性能优化技巧', 'category': '优化技能', 'unlock_level': 7}
            ]
        }

        # 默认技能模板
        default_skills = [
            {'name': '知识储备', 'description': '丰富的专业知识', 'category': '专业技能', 'unlock_level': 1},
            {'name': '沟通表达', 'description': '清晰的沟通表达能力', 'category': '沟通技能', 'unlock_level': 1},
            {'name': '逻辑思维', 'description': '强大的逻辑思维能力', 'category': '思维技能', 'unlock_level': 3},
            {'name': '学习适应', 'description': '快速学习和适应能力', 'category': '学习能力', 'unlock_level': 5},
            {'name': '创新思维', 'description': '创新和创造性思维', 'category': '思维技能', 'unlock_level': 7}
        ]

        return templates.get(role_name, default_skills)