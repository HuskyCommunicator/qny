"""
代码质量检查工具
- 代码规范检查
- 复杂度分析
- 重复代码检测
- 性能问题识别
"""

import ast
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CodeQualityChecker:
    """代码质量检查器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues = []
        self.stats = {
            "total_files": 0,
            "total_lines": 0,
            "complexity_scores": [],
            "duplicated_blocks": [],
            "quality_issues": []
        }

    def check_project(self) -> Dict[str, Any]:
        """检查整个项目的代码质量"""
        python_files = self._find_python_files()
        self.stats["total_files"] = len(python_files)

        for file_path in python_files:
            self._check_file(file_path)

        return {
            "summary": self._generate_summary(),
            "issues": self.issues,
            "statistics": self.stats,
            "recommendations": self._generate_recommendations()
        }

    def _find_python_files(self) -> List[Path]:
        """查找所有Python文件"""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        return python_files

    def _check_file(self, file_path: Path):
        """检查单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.stats["total_lines"] += len(content.splitlines())

            # 语法检查
            self._check_syntax(file_path, content)

            # 代码风格检查
            self._check_style(file_path, content)

            # 复杂度检查
            self._check_complexity(file_path, content)

            # 重复代码检查
            self._check_duplication(file_path, content)

            # 文档检查
            self._check_documentation(file_path, content)

        except Exception as e:
            logger.error(f"检查文件 {file_path} 时出错: {str(e)}")
            self.issues.append({
                "file": str(file_path),
                "line": 0,
                "type": "error",
                "message": f"文件检查失败: {str(e)}",
                "severity": "high"
            })

    def _check_syntax(self, file_path: Path, content: str):
        """检查语法错误"""
        try:
            ast.parse(content)
        except SyntaxError as e:
            self.issues.append({
                "file": str(file_path),
                "line": e.lineno,
                "type": "syntax",
                "message": f"语法错误: {e.msg}",
                "severity": "high"
            })

    def _check_style(self, file_path: Path, content: str):
        """检查代码风格"""
        lines = content.splitlines()

        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()

            # 检查行长度
            if len(line) > 120:
                self.issues.append({
                    "file": str(file_path),
                    "line": line_num,
                    "type": "style",
                    "message": f"行长度超过120字符: {len(line)}字符",
                    "severity": "low"
                })

            # 检查尾随空格
            if line != line.rstrip():
                self.issues.append({
                    "file": str(file_path),
                    "line": line_num,
                    "type": "style",
                    "message": "行尾有空格",
                    "severity": "low"
                })

            # 检查制表符
            if '\t' in line:
                self.issues.append({
                    "file": str(file_path),
                    "line": line_num,
                    "type": "style",
                    "message": "使用制表符而非空格",
                    "severity": "low"
                })

    def _check_complexity(self, file_path: Path, content: str):
        """检查代码复杂度"""
        try:
            tree = ast.parse(content)
            complexity_analyzer = ComplexityAnalyzer()
            complexity_analyzer.visit(tree)

            max_complexity = 10
            for func_name, complexity in complexity_analyzer.complexities.items():
                if complexity > max_complexity:
                    self.issues.append({
                        "file": str(file_path),
                        "line": 0,
                        "type": "complexity",
                        "message": f"函数 {func_name} 复杂度过高: {complexity} (建议 <= {max_complexity})",
                        "severity": "medium"
                    })

                self.stats["complexity_scores"].append(complexity)

        except Exception as e:
            logger.error(f"复杂度检查失败 {file_path}: {str(e)}")

    def _check_duplication(self, file_path: Path, content: str):
        """检查重复代码"""
        # 简化的重复代码检查
        lines = content.splitlines()
        line_groups = {}

        for i, line in enumerate(lines):
            # 忽略空行和注释
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue

            # 创建行签名（简化版本）
            line_signature = self._create_line_signature(stripped)

            if line_signature in line_groups:
                line_groups[line_signature].append((file_path, i + 1, stripped))
            else:
                line_groups[line_signature] = [(file_path, i + 1, stripped)]

        # 检查重复行
        for signature, occurrences in line_groups.items():
            if len(occurrences) > 3:  # 超过3次重复
                self.stats["duplicated_blocks"].append({
                    "signature": signature,
                    "occurrences": occurrences,
                    "count": len(occurrences)
                })

                if len(occurrences) > 5:  # 超过5次才报告
                    self.issues.append({
                        "file": str(file_path),
                        "line": occurrences[0][1],
                        "type": "duplication",
                        "message": f"发现重复代码块，重复 {len(occurrences)} 次",
                        "severity": "low"
                    })

    def _check_documentation(self, file_path: Path, content: str):
        """检查文档完整性"""
        try:
            tree = ast.parse(content)
            doc_checker = DocumentationChecker()
            doc_checker.visit(tree)

            for item in doc_checker.missing_docs:
                self.issues.append({
                    "file": str(file_path),
                    "line": item.get("line", 0),
                    "type": "documentation",
                    "message": f"{item['type']} {item['name']} 缺少文档字符串",
                    "severity": "low"
                })

        except Exception as e:
            logger.error(f"文档检查失败 {file_path}: {str(e)}")

    def _create_line_signature(self, line: str):
        """创建行签名（用于重复代码检测）"""
        # 移除变量名和数字
        signature = re.sub(r'\b[a-zA-Z_]\w*\b', 'VAR', line)
        signature = re.sub(r'\b\d+\b', 'NUM', signature)
        signature = re.sub(r'\s+', ' ', signature).strip()
        return signature

    def _generate_summary(self) -> Dict[str, Any]:
        """生成质量检查摘要"""
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        type_counts = {}

        for issue in self.issues:
            severity_counts[issue["severity"]] += 1
            issue_type = issue["type"]
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1

        avg_complexity = sum(self.stats["complexity_scores"]) / len(self.stats["complexity_scores"]) if self.stats["complexity_scores"] else 0

        return {
            "total_issues": len(self.issues),
            "severity_breakdown": severity_counts,
            "type_breakdown": type_counts,
            "average_complexity": round(avg_complexity, 2),
            "duplicated_blocks": len(self.stats["duplicated_blocks"])
        }

    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []

        summary = self._generate_summary()

        if summary["severity_breakdown"]["high"] > 0:
            recommendations.append("优先修复高严重性问题")

        if summary["average_complexity"] > 15:
            recommendations.append("考虑重构复杂函数，降低圈复杂度")

        if summary["duplicated_blocks"] > 10:
            recommendations.append("提取重复代码到公共函数或类")

        if summary["type_breakdown"].get("documentation", 0) > 5:
            recommendations.append("添加缺失的文档字符串")

        if summary["type_breakdown"].get("style", 0) > 10:
            recommendations.append("统一代码风格，考虑使用自动格式化工具")

        return recommendations


class ComplexityAnalyzer(ast.NodeVisitor):
    """圈复杂度分析器"""

    def __init__(self):
        self.complexities = {}
        self.current_function = None
        self.current_complexity = 1

    def visit_FunctionDef(self, node):
        old_function = self.current_function
        old_complexity = self.current_complexity

        self.current_function = node.name
        self.current_complexity = 1

        self.generic_visit(node)

        self.complexities[self.current_function] = self.current_complexity

        self.current_function = old_function
        self.current_complexity = old_complexity

    def visit_If(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        self.current_complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        # 布尔操作增加复杂度
        self.current_complexity += len(node.values) - 1
        self.generic_visit(node)


class DocumentationChecker(ast.NodeVisitor):
    """文档检查器"""

    def __init__(self):
        self.missing_docs = []

    def visit_FunctionDef(self, node):
        if not ast.get_docstring(node):
            self.missing_docs.append({
                "type": "函数",
                "name": node.name,
                "line": node.lineno
            })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if not ast.get_docstring(node):
            self.missing_docs.append({
                "type": "类",
                "name": node.name,
                "line": node.lineno
            })
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if not ast.get_docstring(node):
            self.missing_docs.append({
                "type": "异步函数",
                "name": node.name,
                "line": node.lineno
            })
        self.generic_visit(node)


def generate_code_documentation(project_root: str) -> Dict[str, Any]:
    """生成代码文档"""
    doc_generator = CodeDocumentationGenerator(project_root)
    return doc_generator.generate()


class CodeDocumentationGenerator:
    """代码文档生成器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def generate(self) -> Dict[str, Any]:
        """生成完整的代码文档"""
        return {
            "api_documentation": self._generate_api_docs(),
            "module_documentation": self._generate_module_docs(),
            "architecture_documentation": self._generate_architecture_docs(),
            "usage_examples": self._generate_usage_examples()
        }

    def _generate_api_docs(self) -> Dict[str, Any]:
        """生成API文档"""
        # 模拟API文档生成
        return {
            "title": "AI角色扮演平台API文档",
            "version": "1.0.0",
            "description": "完整的API接口文档",
            "endpoints": self._extract_api_endpoints()
        }

    def _generate_module_docs(self) -> Dict[str, Any]:
        """生成模块文档"""
        return {
            "core_modules": self._document_core_modules(),
            "service_modules": self._document_service_modules(),
            "router_modules": self._document_router_modules()
        }

    def _generate_architecture_docs(self) -> Dict[str, Any]:
        """生成架构文档"""
        return {
            "overview": "系统架构概述",
            "layers": self._document_architecture_layers(),
            "data_flow": self._document_data_flow(),
            "components": self._document_components()
        }

    def _generate_usage_examples(self) -> Dict[str, Any]:
        """生成使用示例"""
        return {
            "authentication": self._generate_auth_examples(),
            "role_management": self._generate_role_examples(),
            "chat_interaction": self._generate_chat_examples(),
            "recommendation": self._generate_recommendation_examples()
        }

    def _extract_api_endpoints(self) -> List[Dict[str, Any]]:
        """提取API端点信息"""
        endpoints = []

        # 扫描路由文件
        router_files = [
            "auth.py", "chat.py", "role.py", "me.py",
            "recommendation.py", "growth.py", "scene.py"
        ]

        for router_file in router_files:
            file_path = self.project_root / "app" / "routers" / router_file
            if file_path.exists():
                endpoints.extend(self._parse_router_file(file_path))

        return endpoints

    def _parse_router_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """解析路由文件"""
        # 模拟路由解析
        return []

    def _document_core_modules(self) -> List[Dict[str, Any]]:
        """文档化核心模块"""
        return [
            {
                "name": "config",
                "description": "配置管理模块",
                "features": ["环境变量管理", "配置验证", "默认值设置"]
            },
            {
                "name": "security",
                "description": "安全认证模块",
                "features": ["JWT认证", "密码加密", "权限管理"]
            },
            {
                "name": "database",
                "description": "数据库连接模块",
                "features": ["连接池管理", "事务处理", "会话管理"]
            }
        ]

    def _document_service_modules(self) -> List[Dict[str, Any]]:
        """文档化服务模块"""
        return [
            {
                "name": "recommendation_service",
                "description": "智能推荐系统",
                "features": ["协同过滤", "内容过滤", "混合推荐"]
            },
            {
                "name": "growth_service",
                "description": "角色成长系统",
                "features": ["等级计算", "技能系统", "经验值管理"]
            },
            {
                "name": "chat_service",
                "description": "聊天服务",
                "features": ["会话管理", "消息存储", "上下文处理"]
            }
        ]

    def _document_router_modules(self) -> List[Dict[str, Any]]:
        """文档化路由模块"""
        return [
            {
                "name": "auth_router",
                "description": "认证路由",
                "endpoints": ["/register", "/login", "/logout"]
            },
            {
                "name": "chat_router",
                "description": "聊天路由",
                "endpoints": ["/chat/text", "/chat/stt", "/chat/tts"]
            }
        ]

    def _document_architecture_layers(self) -> List[Dict[str, Any]]:
        """文档化架构层级"""
        return [
            {
                "layer": "Presentation Layer",
                "description": "表示层，处理HTTP请求和响应",
                "components": ["FastAPI Router", "Middleware", "Response Format"]
            },
            {
                "layer": "Service Layer",
                "description": "业务逻辑层，处理核心业务逻辑",
                "components": ["Recommendation Engine", "Growth System", "Chat Service"]
            },
            {
                "layer": "Data Access Layer",
                "description": "数据访问层，处理数据库操作",
                "components": ["SQLAlchemy ORM", "Database Models", "Sessions"]
            }
        ]

    def _document_data_flow(self) -> Dict[str, Any]:
        """文档化数据流"""
        return {
            "request_flow": [
                "HTTP Request",
                "Middleware Processing",
                "Authentication",
                "Business Logic",
                "Database Operation",
                "Response Generation"
            ],
            "data_models": ["User", "Role", "ChatSession", "Message", "Feedback"]
        }

    def _document_components(self) -> List[Dict[str, Any]]:
        """文档化组件"""
        return [
            {
                "name": "Recommendation Engine",
                "purpose": "提供个性化角色推荐",
                "dependencies": ["User Service", "Role Service", "Chat Service"]
            },
            {
                "name": "Growth System",
                "purpose": "管理角色成长和等级",
                "dependencies": ["Chat Service", "Feedback Service"]
            }
        ]

    def _generate_auth_examples(self) -> List[Dict[str, Any]]:
        """生成认证示例"""
        return [
            {
                "title": "用户注册",
                "method": "POST",
                "endpoint": "/auth/register",
                "description": "注册新用户账户"
            }
        ]

    def _generate_role_examples(self) -> List[Dict[str, Any]]:
        """生成角色管理示例"""
        return [
            {
                "title": "创建角色",
                "method": "POST",
                "endpoint": "/role/create",
                "description": "创建新的AI角色"
            }
        ]

    def _generate_chat_examples(self) -> List[Dict[str, Any]]:
        """生成聊天示例"""
        return [
            {
                "title": "发送消息",
                "method": "POST",
                "endpoint": "/chat/text",
                "description": "与AI角色进行文本对话"
            }
        ]

    def _generate_recommendation_examples(self) -> List[Dict[str, Any]]:
        """生成推荐示例"""
        return [
            {
                "title": "获取推荐",
                "method": "GET",
                "endpoint": "/recommendation/roles",
                "description": "获取个性化角色推荐"
            }
        ]