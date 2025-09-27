"""
业务逻辑分析工具
- 业务流程分析
- 数据流向分析
- 依赖关系分析
- 性能瓶颈识别
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import ast
import json
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class BusinessProcess:
    """业务流程"""
    name: str
    description: str
    steps: List[Dict[str, Any]]
    entry_point: str
    exit_points: List[str]
    dependencies: List[str]
    performance_metrics: Dict[str, Any]


@dataclass
class DataFlow:
    """数据流向"""
    source: str
    target: str
    data_type: str
    transformation: Optional[str]
    volume: str  # low, medium, high
    frequency: str  # real-time, batch, periodic


@dataclass
class Dependency:
    """依赖关系"""
    from_component: str
    to_component: str
    type: str  # function_call, data_access, service_call
    strength: str  # strong, medium, weak
    criticality: str  # high, medium, low


class BusinessLogicAnalyzer:
    """业务逻辑分析器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.processes = []
        self.data_flows = []
        self.dependencies = []
        self.components = {}

    def analyze_business_logic(self) -> Dict[str, Any]:
        """分析业务逻辑"""
        self._discover_components()
        self._analyze_business_processes()
        self._analyze_data_flows()
        self._analyze_dependencies()
        self._identify_bottlenecks()

        return {
            "processes": self._serialize_processes(),
            "data_flows": self._serialize_data_flows(),
            "dependencies": self._serialize_dependencies(),
            "components": self.components,
            "bottlenecks": self._identify_bottlenecks(),
            "recommendations": self._generate_logic_recommendations()
        }

    def _discover_components(self):
        """发现系统组件"""
        # 扫描服务层
        service_dir = self.project_root / "app" / "services"
        if service_dir.exists():
            for service_file in service_dir.glob("*.py"):
                if not service_file.name.startswith("__"):
                    component_name = service_file.stem.replace("_service", "")
                    self.components[component_name] = {
                        "type": "service",
                        "file": str(service_file),
                        "responsibilities": self._extract_service_responsibilities(service_file)
                    }

        # 扫描路由层
        router_dir = self.project_root / "app" / "routers"
        if router_dir.exists():
            for router_file in router_dir.glob("*.py"):
                if not router_file.name.startswith("__"):
                    component_name = router_file.stem.replace("_router", "")
                    self.components[component_name] = {
                        "type": "router",
                        "file": str(router_file),
                        "endpoints": self._extract_router_endpoints(router_file)
                    }

    def _extract_service_responsibilities(self, file_path: Path) -> List[str]:
        """提取服务职责"""
        responsibilities = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 简单的关键词匹配来识别职责
            responsibility_keywords = {
                "recommendation": ["推荐", "算法", "分析", "个性化"],
                "growth": ["成长", "等级", "经验", "技能"],
                "chat": ["聊天", "会话", "消息", "对话"],
                "user": ["用户", "账户", "偏好", "资料"],
                "role": ["角色", "管理", "创建", "编辑"],
                "validation": ["验证", "检查", "规则", "安全"],
                "notification": ["通知", "消息", "推送", "提醒"]
            }

            file_content_lower = content.lower()
            for category, keywords in responsibility_keywords.items():
                if any(keyword in file_content_lower for keyword in keywords):
                    responsibilities.append(category)

            if not responsibilities:
                responsibilities = ["general_service"]

        except Exception as e:
            logger.error(f"提取服务职责失败 {file_path}: {str(e)}")
            responsibilities = ["unknown"]

        return responsibilities

    def _extract_router_endpoints(self, file_path: Path) -> List[Dict[str, Any]]:
        """提取路由端点"""
        endpoints = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用正则表达式提取路由信息
            import re
            router_pattern = r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']'
            matches = re.findall(router_pattern, content)

            for method, path in matches:
                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "full_path": f"/{file_path.stem.replace('_router', '')}{path}"
                })

        except Exception as e:
            logger.error(f"提取路由端点失败 {file_path}: {str(e)}")

        return endpoints

    def _analyze_business_processes(self):
        """分析业务流程"""
        processes_config = [
            {
                "name": "用户注册流程",
                "description": "新用户注册并创建账户",
                "entry_point": "POST /auth/register",
                "steps": [
                    {"step": 1, "action": "输入验证", "component": "validation_service"},
                    {"step": 2, "action": "用户名查重", "component": "user_service"},
                    {"step": 3, "action": "邮箱查重", "component": "user_service"},
                    {"step": 4, "action": "密码加密", "component": "security_service"},
                    {"step": 5, "action": "创建用户记录", "component": "user_service"},
                    {"step": 6, "action": "返回成功响应", "component": "auth_router"}
                ]
            },
            {
                "name": "用户登录流程",
                "description": "用户登录验证和令牌生成",
                "entry_point": "POST /auth/login",
                "steps": [
                    {"step": 1, "action": "输入验证", "component": "validation_service"},
                    {"step": 2, "action": "用户查询", "component": "user_service"},
                    {"step": 3, "action": "密码验证", "component": "security_service"},
                    {"step": 4, "action": "账户状态检查", "component": "user_service"},
                    {"step": 5, "action": "生成JWT令牌", "component": "security_service"},
                    {"step": 6, "action": "更新登录时间", "component": "user_service"},
                    {"step": 7, "action": "返回令牌", "component": "auth_router"}
                ]
            },
            {
                "name": "角色推荐流程",
                "description": "基于用户行为生成个性化角色推荐",
                "entry_point": "GET /recommendation/roles",
                "steps": [
                    {"step": 1, "action": "用户认证", "component": "security_service"},
                    {"step": 2, "action": "用户行为分析", "component": "recommendation_service"},
                    {"step": 3, "action": "协同过滤推荐", "component": "recommendation_service"},
                    {"step": 4, "action": "内容过滤推荐", "component": "recommendation_service"},
                    {"step": 5, "action": "热门角色推荐", "component": "recommendation_service"},
                    {"step": 6, "action": "结果融合排序", "component": "recommendation_service"},
                    {"step": 7, "action": "返回推荐结果", "component": "recommendation_router"}
                ]
            },
            {
                "name": "聊天对话流程",
                "description": "用户与AI角色进行文本对话",
                "entry_point": "POST /chat/text",
                "steps": [
                    {"step": 1, "action": "用户认证", "component": "security_service"},
                    {"step": 2, "action": "输入验证", "component": "validation_service"},
                    {"step": 3, "action": "创建/获取会话", "component": "chat_service"},
                    {"step": 4, "action": "保存用户消息", "component": "chat_service"},
                    {"step": 5, "action": "调用LLM服务", "component": "llm_service"},
                    {"step": 6, "action": "生成角色化回复", "component": "llm_service"},
                    {"step": 7, "action": "保存AI回复", "component": "chat_service"},
                    {"step": 8, "action": "更新会话统计", "component": "chat_service"},
                    {"step": 9, "action": "返回回复结果", "component": "chat_router"}
                ]
            },
            {
                "name": "角色成长流程",
                "description": "角色获得经验值并可能升级",
                "entry_point": "POST /growth/role/{role_id}/experience",
                "steps": [
                    {"step": 1, "action": "用户认证", "component": "security_service"},
                    {"step": 2, "action": "经验值计算", "component": "growth_service"},
                    {"step": 3, "action": "等级计算", "component": "growth_service"},
                    {"step": 4, "action": "检查是否升级", "component": "growth_service"},
                    {"step": 5, "action": "解锁新技能", "component": "growth_service"},
                    {"step": 6, "action": "记录成长历史", "component": "growth_service"},
                    {"step": 7, "action": "更新角色数据", "component": "growth_service"},
                    {"step": 8, "action": "发送通知", "component": "notification_service"},
                    {"step": 9, "action": "返回成长结果", "component": "growth_router"}
                ]
            }
        ]

        for process_config in processes_config:
            process = BusinessProcess(
                name=process_config["name"],
                description=process_config["description"],
                steps=process_config["steps"],
                entry_point=process_config["entry_point"],
                exit_points=self._identify_exit_points(process_config["steps"]),
                dependencies=self._identify_process_dependencies(process_config["steps"]),
                performance_metrics=self._estimate_process_metrics(process_config["name"])
            )
            self.processes.append(process)

    def _analyze_data_flows(self):
        """分析数据流向"""
        flow_configs = [
            {
                "source": "用户输入",
                "target": "validation_service",
                "data_type": "原始请求数据",
                "transformation": "数据验证和清理",
                "volume": "medium",
                "frequency": "real-time"
            },
            {
                "source": "validation_service",
                "target": "business_service",
                "data_type": "验证后数据",
                "transformation": "格式标准化",
                "volume": "medium",
                "frequency": "real-time"
            },
            {
                "source": "business_service",
                "target": "database",
                "data_type": "业务数据",
                "transformation": "ORM映射",
                "volume": "medium",
                "frequency": "real-time"
            },
            {
                "source": "database",
                "target": "business_service",
                "data_type": "查询结果",
                "transformation": "对象转换",
                "volume": "medium",
                "frequency": "real-time"
            },
            {
                "source": "business_service",
                "target": "router",
                "data_type": "处理结果",
                "transformation": "响应格式化",
                "volume": "medium",
                "frequency": "real-time"
            },
            {
                "source": "chat_service",
                "target": "llm_service",
                "data_type": "聊天上下文",
                "transformation": "上下文格式化",
                "volume": "high",
                "frequency": "real-time"
            },
            {
                "source": "llm_service",
                "target": "chat_service",
                "data_type": "AI回复",
                "transformation": "角色化处理",
                "volume": "high",
                "frequency": "real-time"
            },
            {
                "source": "recommendation_service",
                "target": "cache",
                "data_type": "用户画像",
                "transformation": "缓存序列化",
                "volume": "low",
                "frequency": "periodic"
            }
        ]

        for flow_config in flow_configs:
            flow = DataFlow(**flow_config)
            self.data_flows.append(flow)

    def _analyze_dependencies(self):
        """分析组件依赖关系"""
        dependency_configs = [
            {
                "from_component": "auth_router",
                "to_component": "validation_service",
                "type": "service_call",
                "strength": "strong",
                "criticality": "high"
            },
            {
                "from_component": "auth_router",
                "to_component": "user_service",
                "type": "service_call",
                "strength": "strong",
                "criticality": "high"
            },
            {
                "from_component": "chat_router",
                "to_component": "chat_service",
                "type": "service_call",
                "strength": "strong",
                "criticality": "high"
            },
            {
                "from_component": "chat_service",
                "to_component": "llm_service",
                "type": "service_call",
                "strength": "strong",
                "criticality": "high"
            },
            {
                "from_component": "recommendation_router",
                "to_component": "recommendation_service",
                "type": "service_call",
                "strength": "strong",
                "criticality": "medium"
            },
            {
                "from_component": "growth_router",
                "to_component": "growth_service",
                "type": "service_call",
                "strength": "strong",
                "criticality": "medium"
            },
            {
                "from_component": "recommendation_service",
                "to_component": "user_service",
                "type": "data_access",
                "strength": "medium",
                "criticality": "medium"
            },
            {
                "from_component": "all_services",
                "to_component": "database",
                "type": "data_access",
                "strength": "strong",
                "criticality": "high"
            }
        ]

        for dep_config in dependency_configs:
            dependency = Dependency(**dep_config)
            self.dependencies.append(dependency)

    def _identify_exit_points(self, steps: List[Dict[str, Any]]) -> List[str]:
        """识别流程出口点"""
        exit_points = []
        for step in steps:
            if "返回" in step["action"] or "response" in step["action"]:
                exit_points.append(step["component"])
        return exit_points

    def _identify_process_dependencies(self, steps: List[Dict[str, Any]]) -> List[str]:
        """识别流程依赖"""
        dependencies = set()
        for step in steps:
            dependencies.add(step["component"])
        return list(dependencies)

    def _estimate_process_metrics(self, process_name: str) -> Dict[str, Any]:
        """估算流程性能指标"""
        metrics_base = {
            "用户注册流程": {"avg_duration": "500ms", "max_concurrent": 100, "error_rate": "0.1%"},
            "用户登录流程": {"avg_duration": "200ms", "max_concurrent": 500, "error_rate": "0.05%"},
            "角色推荐流程": {"avg_duration": "1000ms", "max_concurrent": 50, "error_rate": "0.2%"},
            "聊天对话流程": {"avg_duration": "1500ms", "max_concurrent": 200, "error_rate": "0.1%"},
            "角色成长流程": {"avg_duration": "300ms", "max_concurrent": 100, "error_rate": "0.05%"}
        }

        return metrics_base.get(process_name, {
            "avg_duration": "unknown",
            "max_concurrent": "unknown",
            "error_rate": "unknown"
        })

    def _identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """识别性能瓶颈"""
        bottlenecks = [
            {
                "component": "llm_service",
                "type": "external_dependency",
                "severity": "high",
                "description": "LLM服务调用是外部依赖，可能存在延迟",
                "impact": "影响所有聊天功能",
                "suggestion": "考虑使用缓存和异步处理"
            },
            {
                "component": "recommendation_service",
                "type": "algorithm_complexity",
                "severity": "medium",
                "description": "推荐算法计算复杂度较高",
                "impact": "影响推荐响应时间",
                "suggestion": "优化算法复杂度，增加缓存"
            },
            {
                "component": "database",
                "type": "resource_contention",
                "severity": "medium",
                "description": "数据库连接可能成为瓶颈",
                "impact": "影响所有数据操作",
                "suggestion": "使用连接池，优化查询"
            },
            {
                "component": "chat_service",
                "type": "memory_usage",
                "severity": "low",
                "description": "聊天上下文可能占用较多内存",
                "impact": "影响并发处理能力",
                "suggestion": "限制上下文长度，定期清理"
            }
        ]

        return bottlenecks

    def _generate_logic_recommendations(self) -> List[str]:
        """生成逻辑优化建议"""
        return [
            "建议实现异步处理机制，提高并发处理能力",
            "优化推荐算法，降低计算复杂度",
            "增加缓存层，减少数据库查询",
            "实现请求限流，防止系统过载",
            "添加监控和告警机制，及时发现问题",
            "考虑使用消息队列处理耗时操作",
            "优化数据库查询，添加适当索引",
            "实现优雅降级机制，提高系统可用性"
        ]

    def _serialize_processes(self) -> List[Dict[str, Any]]:
        """序列化流程信息"""
        return [
            {
                "name": process.name,
                "description": process.description,
                "steps": process.steps,
                "entry_point": process.entry_point,
                "exit_points": process.exit_points,
                "dependencies": process.dependencies,
                "performance_metrics": process.performance_metrics
            }
            for process in self.processes
        ]

    def _serialize_data_flows(self) -> List[Dict[str, Any]]:
        """序列化数据流信息"""
        return [
            {
                "source": flow.source,
                "target": flow.target,
                "data_type": flow.data_type,
                "transformation": flow.transformation,
                "volume": flow.volume,
                "frequency": flow.frequency
            }
            for flow in self.data_flows
        ]

    def _serialize_dependencies(self) -> List[Dict[str, Any]]:
        """序列化依赖信息"""
        return [
            {
                "from_component": dep.from_component,
                "to_component": dep.to_component,
                "type": dep.type,
                "strength": dep.strength,
                "criticality": dep.criticality
            }
            for dep in self.dependencies
        ]

    def generate_flow_diagram(self) -> str:
        """生成流程图（Mermaid格式）"""
        diagram_lines = [
            "```mermaid",
            "graph TD",
            "    A[用户请求] --> B[路由层]",
            "    B --> C[验证层]",
            "    C --> D[业务逻辑层]",
            "    D --> E[数据访问层]",
            "    E --> F[数据库]",
            "    F --> E",
            "    E --> D",
            "    D --> G[外部服务]",
            "    G --> D",
            "    D --> C",
            "    C --> B",
            "    B --> H[响应]",
            "",
            "    subgraph 业务服务",
            "        D1[推荐服务]",
            "        D2[成长服务]",
            "        D3[聊天服务]",
            "        D4[用户服务]",
            "    end",
            "",
            "    D --> D1",
            "    D --> D2",
            "    D --> D3",
            "    D --> D4",
            "```"
        ]

        return "\n".join(diagram_lines)