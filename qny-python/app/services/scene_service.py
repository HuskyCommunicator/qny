from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime
import uuid
import json
import random

from ..models import (
    User, Role, SceneTemplate, SceneSession, SceneParticipant,
    SceneMessage, SceneInteractionRule, SceneRecommendation,
    SceneType, SceneStatus
)
from ..schemas.scene import ParticipantType, MessageType
from ..schemas.scene import (
    SceneSessionCreate, SceneSessionUpdate, SceneSessionOut,
    SceneParticipantCreate, SceneParticipantUpdate, SceneParticipantOut,
    SceneMessageCreate, SceneMessageOut, SceneResponse,
    SceneMessageRequest, SceneStats, SceneRecommendationResponse
)
from ..services.llm_service import generate_reply
from ..scene_templates import (
    SCENE_TEMPLATES, INTERACTION_RULES, ROLE_INTERACTION_STYLES,
    MULTI_ROLE_RESPONSE_STRATEGIES, SCENE_TRANSITION_STRATEGIES
)

class SceneService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: int, session_data: SceneSessionCreate) -> SceneSession:
        """创建多角色对话场景会话"""
        # 验证模板是否存在
        template = self.db.query(SceneTemplate).filter(
            SceneTemplate.id == session_data.template_id,
            SceneTemplate.is_active == True
        ).first()
        if not template:
            raise ValueError("场景模板不存在或已禁用")

        # 创建会话
        session = SceneSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            template_id=session_data.template_id,
            name=session_data.name,
            description=session_data.description,
            config=session_data.config or {},
            status=SceneStatus.ACTIVE
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return session

    def get_session(self, session_id: int) -> Optional[SceneSession]:
        """获取场景会话"""
        return self.db.query(SceneSession).filter(SceneSession.id == session_id).first()

    def get_session_by_uuid(self, session_uuid: str) -> Optional[SceneSession]:
        """通过UUID获取场景会话"""
        return self.db.query(SceneSession).filter(
            SceneSession.session_id == session_uuid
        ).first()

    def get_user_sessions(self, user_id: int, page: int = 1, size: int = 10) -> Tuple[List[SceneSession], int]:
        """获取用户的场景会话列表"""
        offset = (page - 1) * size

        query = self.db.query(SceneSession).filter(
            SceneSession.user_id == user_id
        ).order_by(desc(SceneSession.updated_at))

        total = query.count()
        sessions = query.offset(offset).limit(size).all()

        return sessions, total

    def add_participant(self, session_id: int, participant_data: SceneParticipantCreate) -> SceneParticipant:
        """添加场景参与者"""
        # 验证会话是否存在
        session = self.get_session(session_id)
        if not session:
            raise ValueError("场景会话不存在")

        # 验证角色是否存在
        role = self.db.query(Role).filter(Role.id == participant_data.role_id).first()
        if not role:
            raise ValueError("角色不存在")

        # 检查角色是否已经在会话中
        existing = self.db.query(SceneParticipant).filter(
            and_(
                SceneParticipant.session_id == session_id,
                SceneParticipant.role_id == participant_data.role_id
            )
        ).first()
        if existing:
            raise ValueError("角色已经在会话中")

        # 检查是否超过最大角色数量
        participant_count = self.db.query(SceneParticipant).filter(
            SceneParticipant.session_id == session_id
        ).count()

        # 获取模板信息检查最大角色数量限制
        template = self.db.query(SceneTemplate).filter(SceneTemplate.id == session.template_id).first()
        if template and participant_count >= template.max_roles:
            raise ValueError(f"会话角色数量已达到最大限制({template.max_roles})")

        # 获取加入顺序
        max_order = self.db.query(func.max(SceneParticipant.join_order)).filter(
            SceneParticipant.session_id == session_id
        ).scalar() or 0

        participant = SceneParticipant(
            session_id=session_id,
            role_id=participant_data.role_id,
            participant_type=participant_data.participant_type,
            join_order=max_order + 1,
            personality_config=participant_data.personality_config or {}
        )

        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)

        return participant

    def get_session_participants(self, session_id: int) -> List[SceneParticipant]:
        """获取会话参与者列表"""
        return self.db.query(SceneParticipant).filter(
            SceneParticipant.session_id == session_id
        ).order_by(SceneParticipant.join_order).all()

    def get_active_participants(self, session_id: int) -> List[SceneParticipant]:
        """获取活跃的会话参与者"""
        return self.db.query(SceneParticipant).filter(
            and_(
                SceneParticipant.session_id == session_id,
                SceneParticipant.is_active == True
            )
        ).order_by(SceneParticipant.join_order).all()

    def remove_participant(self, participant_id: int) -> bool:
        """移除场景参与者"""
        participant = self.db.query(SceneParticipant).filter(
            SceneParticipant.id == participant_id
        ).first()

        if participant:
            participant.is_active = False
            self.db.commit()
            return True
        return False

    def send_message(self, user_id: int, message_data: SceneMessageRequest) -> SceneResponse:
        """发送多角色对话消息"""
        # 验证会话存在且属于用户
        session = self.get_session(message_data.session_id)
        if not session or session.user_id != user_id:
            raise ValueError("会话不存在或无权限")

        if session.status != SceneStatus.ACTIVE:
            raise ValueError("会话未激活")

        # 获取会话参与者
        participants = self.get_active_participants(message_data.session_id)
        if not participants:
            raise ValueError("会话中没有活跃的参与者")

        # 保存用户消息
        user_participant = self.db.query(SceneParticipant).filter(
            and_(
                SceneParticipant.session_id == message_data.session_id,
                SceneParticipant.participant_type == ParticipantType.USER
            )
        ).first()

        if not user_participant:
            # 创建用户参与者
            user_participant = SceneParticipant(
                session_id=message_data.session_id,
                role_id=1,  # 使用默认用户角色
                participant_type=ParticipantType.USER,
                join_order=0
            )
            self.db.add(user_participant)
            self.db.commit()
            self.db.refresh(user_participant)

        # 保存用户消息
        user_message = SceneMessage(
            session_id=message_data.session_id,
            participant_id=user_participant.id,
            role_id=user_participant.role_id,
            message_type=message_data.message_type,
            content=message_data.content,
            context=message_data.context or {}
        )
        self.db.add(user_message)

        # 生成AI回复
        ai_messages = self._generate_ai_responses(
            session, participants, message_data.content, message_data.context
        )

        # 保存AI回复
        saved_messages = []
        for ai_message in ai_messages:
            saved_message = SceneMessage(
                session_id=message_data.session_id,
                participant_id=ai_message['participant_id'],
                role_id=ai_message['role_id'],
                message_type=MessageType.TEXT,
                content=ai_message['content'],
                context=ai_message.get('context', {})
            )
            self.db.add(saved_message)
            saved_messages.append(saved_message)

        # 更新会话消息计数
        session.message_count += len(saved_messages) + 1
        session.updated_at = datetime.utcnow()

        # 更新当前发言者
        if saved_messages:
            session.current_speaker = saved_messages[-1].role_id

        self.db.commit()

        # 返回响应
        return self._build_scene_response(session, saved_messages)

    def _generate_ai_responses(self, session: SceneSession, participants: List[SceneParticipant],
                             user_message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """生成AI回复"""
        responses = []

        # 获取会话策略
        template_config = session.template.config or {}
        strategy_name = template_config.get('response_strategy', 'sequential')

        if strategy_name == 'sequential':
            responses = self._generate_sequential_responses(participants, user_message, context)
        elif strategy_name == 'expertise_based':
            responses = self._generate_expertise_responses(participants, user_message, context)
        elif strategy_name == 'collaborative':
            responses = self._generate_collaborative_responses(participants, user_message, context)
        else:
            # 默认使用顺序回复
            responses = self._generate_sequential_responses(participants, user_message, context)

        return responses

    def _generate_sequential_responses(self, participants: List[SceneParticipant],
                                     user_message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """顺序回复策略"""
        responses = []

        # 选择下一个发言者
        current_speaker = None
        if context and 'current_speaker' in context:
            current_speaker = context['current_speaker']

        # 获取AI参与者
        ai_participants = [p for p in participants if p.participant_type == ParticipantType.AI]
        if not ai_participants:
            return responses

        # 找到下一个发言者
        next_speaker = None
        if current_speaker:
            current_index = -1
            for i, participant in enumerate(ai_participants):
                if participant.role_id == current_speaker:
                    current_index = i
                    break

            next_index = (current_index + 1) % len(ai_participants)
            next_speaker = ai_participants[next_index]
        else:
            next_speaker = ai_participants[0]

        # 生成回复
        role = next_speaker.role
        role_response = generate_reply(
            messages=[{"role": "user", "content": user_message}],
            role_id=role.id,
            db=self.db
        )

        # 应用角色互动风格
        interaction_style = ROLE_INTERACTION_STYLES.get(role.name, {})
        if interaction_style:
            response_content = self._apply_interaction_style(role_response, interaction_style)
        else:
            response_content = role_response

        responses.append({
            'participant_id': next_speaker.id,
            'role_id': role.id,
            'content': response_content,
            'context': {'strategy': 'sequential', 'speaker_rotation': [p.role_id for p in ai_participants]}
        })

        return responses

    def _generate_expertise_responses(self, participants: List[SceneParticipant],
                                     user_message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """专业匹配回复策略"""
        responses = []

        # 关键词与角色匹配
        expertise_keywords = {
            '哲学': ['苏格拉底'],
            '科学': ['爱因斯坦'],
            '魔法': ['哈利波特'],
            '推理': ['夏洛克·福尔摩斯'],
            '心理': ['心理咨询师'],
            '编程': ['编程助手', 'Python编程助手'],
            '前端': ['前端开发顾问']
        }

        # 匹配最合适的角色
        best_role = None
        for keyword, role_names in expertise_keywords.items():
            if keyword in user_message:
                for participant in participants:
                    if participant.role.name in role_names:
                        best_role = participant
                        break
                if best_role:
                    break

        if not best_role:
            # 如果没有匹配，随机选择一个AI角色
            ai_participants = [p for p in participants if p.participant_type == ParticipantType.AI]
            if ai_participants:
                best_role = random.choice(ai_participants)

        if best_role:
            role_response = generate_reply(
                messages=[{"role": "user", "content": user_message}],
                role_id=best_role.role.id,
                db=self.db
            )

            responses.append({
                'participant_id': best_role.id,
                'role_id': best_role.role.id,
                'content': role_response,
                'context': {'strategy': 'expertise_based', 'matched_keyword': 'keyword'}
            })

        return responses

    def _generate_collaborative_responses(self, participants: List[SceneParticipant],
                                       user_message: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """协作回复策略"""
        responses = []

        # 选择2-3个AI角色进行协作回复
        ai_participants = [p for p in participants if p.participant_type == ParticipantType.AI]
        if len(ai_participants) < 2:
            return self._generate_sequential_responses(participants, user_message, context)

        # 选择前两个角色
        selected_participants = ai_participants[:2]

        # 生成第一个角色的回复（主要观点）
        first_response = generate_reply(
            messages=[{"role": "user", "content": user_message}],
            role_id=selected_participants[0].role.id,
            db=self.db
        )

        # 生成第二个角色的回复（补充观点）
        follow_up_prompt = f"对于用户的问题'{user_message}'，前面已经回复了'{first_response}'，请你补充一些观点。"
        second_response = generate_reply(
            messages=[{"role": "user", "content": follow_up_prompt}],
            role_id=selected_participants[1].role.id,
            db=self.db
        )

        responses.extend([
            {
                'participant_id': selected_participants[0].id,
                'role_id': selected_participants[0].role.id,
                'content': first_response,
                'context': {'strategy': 'collaborative', 'role': 'primary'}
            },
            {
                'participant_id': selected_participants[1].id,
                'role_id': selected_participants[1].role.id,
                'content': second_response,
                'context': {'strategy': 'collaborative', 'role': 'supplementary'}
            }
        ])

        return responses

    def _apply_interaction_style(self, response: str, style_config: Dict[str, Any]) -> str:
        """应用角色互动风格"""
        patterns = style_config.get('interaction_patterns', [])
        if patterns and random.random() < 0.3:  # 30%概率使用互动模式
            pattern = random.choice(patterns)
            return f"{pattern}\n\n{response}"
        return response

    def _build_scene_response(self, session: SceneSession, messages: List[SceneMessage]) -> SceneResponse:
        """构建场景响应"""
        # 获取参与者信息
        participants = self.get_session_participants(session.id)

        # 构建消息详情
        message_details = []
        for message in messages:
            participant = next((p for p in participants if p.id == message.participant_id), None)
            message_details.append({
                'id': message.id,
                'participant_id': message.participant_id,
                'role_id': message.role_id,
                'content': message.content,
                'message_type': message.message_type,
                'created_at': message.created_at,
                'participant': {
                    'id': participant.id if participant else None,
                    'role_id': participant.role_id if participant else None,
                    'role_name': participant.role.name if participant else None,
                    'participant_type': participant.participant_type if participant else None,
                    'speak_count': participant.speak_count if participant else None,
                    'is_active': participant.is_active if participant else None
                } if participant else None
            })

        # 构建发言轮转列表
        active_participants = [p for p in participants if p.is_active and p.participant_type == ParticipantType.AI]
        speaker_rotation = [p.role_id for p in active_participants]

        # 生成建议回复
        suggestions = self._generate_response_suggestions(session, messages)

        return SceneResponse(
            session_id=session.id,
            messages=message_details,
            current_speaker=session.current_speaker,
            speaker_rotation=speaker_rotation,
            suggestions=suggestions
        )

    def _generate_response_suggestions(self, session: SceneSession, messages: List[SceneMessage]) -> Optional[List[str]]:
        """生成回复建议"""
        if not messages:
            return None

        suggestions = [
            "我想听听其他角色的看法",
            "能详细解释一下吗？",
            "有什么具体的例子吗？",
            "这个观点很有意思，请继续",
            "从不同角度来分析一下"
        ]

        # 根据场景类型定制建议
        if session.template.scene_type == SceneType.TEACHING:
            suggestions.extend([
                "这个知识点很重要，能重复一下吗？",
                "有什么实践练习建议吗？"
            ])
        elif session.template.scene_type == SceneType.DISCUSSION:
            suggestions.extend([
                "我们来深入讨论一下这个观点",
                "有没有不同的看法？"
            ])

        return random.sample(suggestions, min(3, len(suggestions)))

    def get_session_messages(self, session_id: int, page: int = 1, size: int = 50) -> Tuple[List[SceneMessage], int]:
        """获取会话消息"""
        offset = (page - 1) * size

        query = self.db.query(SceneMessage).filter(
            SceneMessage.session_id == session_id
        ).order_by(SceneMessage.created_at)

        total = query.count()
        messages = query.offset(offset).limit(size).all()

        return messages, total

    def end_session(self, session_id: int) -> bool:
        """结束会话"""
        session = self.get_session(session_id)
        if session:
            session.status = SceneStatus.ENDED
            session.ended_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def get_scene_stats(self, user_id: int) -> SceneStats:
        """获取场景统计信息"""
        # 基础统计
        total_sessions = self.db.query(SceneSession).filter(
            SceneSession.user_id == user_id
        ).count()

        active_sessions = self.db.query(SceneSession).filter(
            and_(
                SceneSession.user_id == user_id,
                SceneSession.status == SceneStatus.ACTIVE
            )
        ).count()

        total_messages = self.db.query(SceneMessage).join(SceneSession).filter(
            SceneSession.user_id == user_id
        ).count()

        # 热门模板统计
        popular_templates = self.db.query(
            SceneTemplate.title,
            func.count(SceneSession.id).label('usage_count')
        ).join(SceneSession).filter(
            SceneSession.user_id == user_id
        ).group_by(SceneTemplate.title).order_by(
            desc('usage_count')
        ).limit(5).all()

        # 角色参与统计
        role_participation = self.db.query(
            Role.name,
            func.count(SceneParticipant.id).label('participation_count')
        ).join(SceneParticipant).join(SceneSession).filter(
            SceneSession.user_id == user_id
        ).group_by(Role.name).order_by(
            desc('participation_count')
        ).limit(10).all()

        return SceneStats(
            total_sessions=total_sessions,
            active_sessions=active_sessions,
            total_messages=total_messages,
            popular_templates=[
                {'template': t.title, 'count': t.usage_count}
                for t in popular_templates
            ],
            role_participation=[
                {'role': r.name, 'count': r.participation_count}
                for r in role_participation
            ]
        )

    def initialize_templates(self):
        """初始化场景模板数据"""
        for template_data in SCENE_TEMPLATES:
            # 检查模板是否已存在
            existing = self.db.query(SceneTemplate).filter(
                SceneTemplate.name == template_data['name']
            ).first()

            if not existing:
                template = SceneTemplate(**template_data)
                self.db.add(template)

        self.db.commit()
        print("场景模板初始化完成")