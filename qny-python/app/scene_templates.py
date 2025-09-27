# 多角色对话场景模板

# 预设场景模板
SCENE_TEMPLATES = [
    {
        "name": "philosophy_discussion",
        "title": "哲学圆桌讨论",
        "description": "邀请哲学大师们探讨人生、道德和存在意义等深刻话题",
        "scene_type": "discussion",
        "max_roles": 4,
        "min_roles": 2,
        "config": {
            "topic": "人生的意义",
            "moderator": "苏格拉底",
            "rules": [
                "每人发言时间不超过3分钟",
                "需要用提问的方式引导思考",
                "可以引用经典哲学著作"
            ],
            "atmosphere": "严肃但友好"
        }
    },
    {
        "name": "science_teaching",
        "title": "科学教学课堂",
        "description": "爱因斯坦和牛顿等科学家共同讲解科学原理和发现",
        "scene_type": "teaching",
        "max_roles": 3,
        "min_roles": 2,
        "config": {
            "subject": "物理学基础",
            "difficulty": "初级",
            "teaching_style": "互动式",
            "topics": [
                "相对论基础",
                "经典力学",
                "量子力学入门"
            ],
            "interactive": True
        }
    },
    {
        "name": "magic_class",
        "title": "魔法课堂",
        "description": "哈利波特和邓布利多教授魔法知识和技能",
        "scene_type": "teaching",
        "max_roles": 3,
        "min_roles": 2,
        "config": {
            "subjects": [
                "基础咒语",
                "魔法史",
                "魔药学"
            ],
            "difficulty": "初级到中级",
            "practical": True,
            "safety_rules": [
                "不要练习危险咒语",
                "在教授指导下操作"
            ]
        }
    },
    {
        "name": "detective_debate",
        "title": "侦探推理辩论",
        "description": "福尔摩斯和华生共同分析案件线索和推理",
        "scene_type": "debate",
        "max_roles": 4,
        "min_roles": 2,
        "config": {
            "case_type": "神秘失踪案",
            "evidence": [
                "血迹样本",
                "目击者证词",
                "物证分析"
            ],
            "debate_rules": [
                "基于证据推理",
                "提出合理假设",
                "互相质疑和验证"
            ]
        }
    },
    {
        "name": "psychology_session",
        "title": "心理咨询会话",
        "description": "心理咨询师和人生导师共同提供情感支持和建议",
        "scene_type": "collaboration",
        "max_roles": 3,
        "min_roles": 2,
        "config": {
            "focus": "情感问题",
            "approach": "多角度分析",
            "techniques": [
                "认知行为疗法",
                "积极心理学",
                "情绪管理"
            ],
            "environment": "安全、支持性"
        }
    },
    {
        "name": "tech_innovation",
        "title": "技术创新讨论",
        "description": "编程专家和前端顾问讨论最新技术趋势",
        "scene_type": "discussion",
        "max_roles": 4,
        "min_roles": 2,
        "config": {
            "topics": [
                "人工智能",
                "前端框架",
                "云计算",
                "区块链"
            ],
            "format": "技术分享和讨论",
            "level": "中级到高级"
        }
    },
    {
        "name": "literature_salon",
        "title": "文学沙龙",
        "description": "文学家和诗人们讨论文学作品和创作心得",
        "scene_type": "entertainment",
        "max_roles": 5,
        "min_roles": 2,
        "config": {
            "theme": "现代文学",
            "activities": [
                "作品赏析",
                "创作经验分享",
                "文学批评"
            ],
            "atmosphere": "优雅、富有启发性"
        }
    },
    {
        "name": "business_strategy",
        "title": "商业策略会议",
        "description": "商业专家和企业家讨论商业策略和市场竞争",
        "scene_type": "collaboration",
        "max_roles": 4,
        "min_roles": 2,
        "config": {
            "focus": "创业和投资",
            "topics": [
                "市场分析",
                "团队建设",
                "融资策略",
                "风险管理"
            ],
            "style": "务实、结果导向"
        }
    }
]

# 场景互动规则模板
INTERACTION_RULES = {
    "discussion": [
        {
            "name": "轮流发言",
            "rule_type": "turn_based",
            "condition": {"type": "message_received"},
            "action": {"type": "rotate_speaker"},
            "priority": 1
        },
        {
            "name": "主题引导",
            "rule_type": "topic_focus",
            "condition": {"type": "off_topic"},
            "action": {"type": "remind_topic"},
            "priority": 2
        }
    ],
    "teaching": [
        {
            "name": "教学优先",
            "rule_type": "teacher_priority",
            "condition": {"type": "question_asked"},
            "action": {"type": "teacher_respond"},
            "priority": 1
        },
        {
            "name": "进度控制",
            "rule_type": "pace_control",
            "condition": {"type": "progress_check"},
            "action": {"type": "adjust_pace"},
            "priority": 2
        }
    ],
    "debate": [
        {
            "name": "对立观点",
            "rule_type": "opposing_views",
            "condition": {"type": "consensus_reached"},
            "action": {"type": "introduce_opposition"},
            "priority": 1
        },
        {
            "name": "证据要求",
            "rule_type": "evidence_required",
            "condition": {"type": "claim_made"},
            "action": {"type": "request_evidence"},
            "priority": 2
        }
    ],
    "collaboration": [
        {
            "name": "合作建设",
            "rule_type": "collaborative_building",
            "condition": {"type": "idea_presented"},
            "action": {"type": "build_upon"},
            "priority": 1
        },
        {
            "name": "总结综合",
            "rule_type": "synthesis",
            "condition": {"type": "discussion_complete"},
            "action": {"type": "create_summary"},
            "priority": 3
        }
    ],
    "entertainment": [
        {
            "name": "氛围营造",
            "rule_type": "atmosphere_creation",
            "condition": {"type": "low_energy"},
            "action": {"type": "boost_atmosphere"},
            "priority": 1
        },
        {
            "name": "互动游戏",
            "rule_type": "interactive_games",
            "condition": {"type": "routine_detected"},
            "action": {"type": "introduce_game"},
            "priority": 2
        }
    ]
}

# 角色互动风格
ROLE_INTERACTION_STYLES = {
    "苏格拉底": {
        "style": "提问式",
        "characteristics": [
            "喜欢用提问引导思考",
            "避免直接给出答案",
            "鼓励对方自己得出结论"
        ],
        "interaction_patterns": [
            "你的观点是基于什么假设？",
            "你能举一个具体的例子吗？",
            "这个想法会导致什么结果？"
        ]
    },
    "爱因斯坦": {
        "style": "启发式",
        "characteristics": [
            "用简单的比喻解释复杂概念",
            "强调想象力和创造力",
            "鼓励突破传统思维"
        ],
        "interaction_patterns": [
            "想象一下，如果...",
            "从另一个角度来看...",
            "这个问题让我想到了..."
        ]
    },
    "哈利波特": {
        "style": "热情友好",
        "characteristics": [
            "充满好奇心",
            "喜欢分享亲身经历",
            "鼓励实践和尝试"
        ],
        "interaction_patterns": [
            "我在霍格沃茨学到了...",
            "让我告诉你一个有趣的故事...",
            "你也来试试看！"
        ]
    },
    "夏洛克·福尔摩斯": {
        "style": "逻辑推理",
        "characteristics": [
            "注重细节和证据",
            "用逻辑链分析问题",
            "排除不可能的选项"
        ],
        "interaction_patterns": [
            "从现有的证据来看...",
            "我们需要考虑所有的可能性",
            "这个线索告诉我们..."
        ]
    },
    "心理咨询师": {
        "style": "支持倾听",
        "characteristics": [
            "积极倾听和理解",
            "提供情感支持",
            "帮助建立自信"
        ],
        "interaction_patterns": [
            "我能理解你的感受...",
            "你已经在努力了，这很棒",
            "我们可以一起找到解决方法"
        ]
    }
}

# 场景切换策略
SCENE_TRANSITION_STRATEGIES = {
    "smooth": {
        "description": "平滑过渡",
        "method": "gradual_topic_shift",
        "examples": [
            "关于这个话题，我想听听其他角色的看法...",
            "让我们从另一个角度来思考这个问题..."
        ]
    },
    "direct": {
        "description": "直接切换",
        "method": "explicit_topic_change",
        "examples": [
            "现在让我们讨论下一个话题...",
            "转换一下思路，我们来谈谈..."
        ]
    },
    "interactive": {
        "description": "互动切换",
        "method": "audience_engagement",
        "examples": [
            "大家觉得接下来应该讨论什么？",
            "有没有其他想了解的内容？"
        ]
    }
}

# 多角色回复策略
MULTI_ROLE_RESPONSE_STRATEGIES = {
    "sequential": {
        "name": "顺序回复",
        "description": "角色按顺序依次回复",
        "implementation": "按加入顺序循环"
    },
    "expertise_based": {
        "name": "专业匹配",
        "description": "根据问题内容选择最专业的角色回复",
        "implementation": "关键词匹配角色专长"
    },
    "personality_based": {
        "name": "性格驱动",
        "description": "根据角色性格特点选择回复方式",
        "implementation": "性格特征分析"
    },
    "collaborative": {
        "name": "协作回复",
        "description": "多个角色协作完成一个回答",
        "implementation": "角色间信息传递和补充"
    }
}

# 场景推荐算法
SCENE_RECOMMATION_ALGORITHMS = {
    "user_preference": {
        "name": "用户偏好",
        "factors": [
            "历史使用频率",
            "用户评分",
            "停留时间"
        ]
    },
    "role_compatibility": {
        "name": "角色兼容性",
        "factors": [
            "角色性格匹配度",
            "专业领域互补性",
            "互动风格协调性"
        ]
    },
    "content_relevance": {
        "name": "内容相关性",
        "factors": [
            "话题相关性",
            "难度匹配度",
            "学习目标一致性"
        ]
    },
    "social_dynamics": {
        "name": "社交动态",
        "factors": [
            "参与度预测",
            "互动质量预期",
            "用户满意度预估"
        ]
    }
}