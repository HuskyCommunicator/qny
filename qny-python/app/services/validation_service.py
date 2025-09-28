"""
数据验证服务
- 输入数据验证
- 业务规则验证
- 数据完整性检查
- 安全性验证
"""

from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime, timedelta
from pydantic import BaseModel, ValidationError as PydanticValidationError
from sqlalchemy.orm import Session
import re
import json
import html
from urllib.parse import urlparse

from ..core.exceptions import ValidationError, BusinessLogicError
from ..utils.helpers import validate_email, validate_password


class ValidationService:
    """数据验证服务"""

    def __init__(self, db: Session):
        self.db = db

    def validate_model_data(self, model_class: Type[BaseModel], data: Dict[str, Any]) -> BaseModel:
        """验证Pydantic模型数据"""
        try:
            return model_class.model_validate(data)
        except PydanticValidationError as e:
            error_messages = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                error_messages.append(f"{field}: {message}")

            raise ValidationError(f"数据验证失败: {'; '.join(error_messages)}")

    def sanitize_string_input(self, input_string: str, max_length: int = 1000, allow_html: bool = False) -> str:
        """清理字符串输入"""
        if not isinstance(input_string, str):
            raise ValidationError("输入必须是字符串")

        # 去除首尾空格
        cleaned = input_string.strip()

        # 限制长度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]

        if not allow_html:
            # 移除HTML标签
            cleaned = re.sub(r'<[^>]+>', '', cleaned)

        # 转义特殊字符
        cleaned = html.escape(cleaned)

        # 移除潜在的危险字符
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'onclick=',
            r'onmouseover=',
            r'data:',
            r'file:',
            r'ftp:',
        ]

        for pattern in dangerous_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        return cleaned

    def validate_email_format(self, email: str) -> bool:
        """验证邮箱格式"""
        if not isinstance(email, str):
            return False

        # 基本格式验证
        if not validate_email(email):
            return False

        # 检查长度
        if len(email) > 254:
            return False

        # 检查邮箱域名
        domain = email.split('@')[-1]
        if not domain or '.' not in domain:
            return False

        # 检查域名格式
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            return False

        return True

    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """验证密码强度"""
        if not isinstance(password, str):
            raise ValidationError("密码必须是字符串")

        validation_result = validate_password(password)
        return validation_result

    def validate_username(self, username: str) -> Dict[str, Any]:
        """验证用户名"""
        errors = []

        # 基本检查
        if not isinstance(username, str):
            errors.append("用户名必须是字符串")
            return {"is_valid": False, "errors": errors}

        # 长度检查
        if len(username) < 3:
            errors.append("用户名至少需要3个字符")
        elif len(username) > 50:
            errors.append("用户名不能超过50个字符")

        # 字符检查
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            errors.append("用户名只能包含字母、数字、下划线和中文")

        # 特殊字符检查
        if username.startswith('_') or username.endswith('_'):
            errors.append("用户名不能以下划线开头或结尾")

        # 连续下划线检查
        if '__' in username:
            errors.append("用户名不能包含连续的下划线")

        # 保留用户名检查
        reserved_usernames = ['admin', 'administrator', 'root', 'system', 'support', 'help']
        if username.lower() in reserved_usernames:
            errors.append("该用户名已被保留")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }

    def validate_url(self, url: str, allowed_schemes: List[str] = None) -> bool:
        """验证URL格式"""
        if not isinstance(url, str):
            return False

        if not url:
            return False

        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            if allowed_schemes and parsed.scheme not in allowed_schemes:
                return False

            return True
        except Exception:
            return False

    def validate_json_data(self, json_string: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证JSON数据"""
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValidationError(f"JSON格式错误: {str(e)}")

        if schema:
            self.validate_json_schema(data, schema)

        return data

    def validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """验证JSON Schema"""
        # 简化的schema验证
        required_fields = schema.get('required', [])
        optional_fields = schema.get('optional', [])
        field_types = schema.get('types', {})

        # 检查必需字段
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"缺少必需字段: {field}")

        # 检查字段类型
        for field, expected_type in field_types.items():
            if field in data:
                if not isinstance(data[field], expected_type):
                    raise ValidationError(f"字段 {field} 类型错误，期望 {expected_type.__name__}")

        return True

    def validate_date_range(self, start_date: datetime, end_date: datetime) -> bool:
        """验证日期范围"""
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValidationError("日期格式错误")

        if start_date > end_date:
            raise ValidationError("开始日期不能晚于结束日期")

        # 检查日期范围是否合理（不超过100年）
        max_range = timedelta(days=365 * 100)
        if end_date - start_date > max_range:
            raise ValidationError("日期范围过大")

        return True

    def validate_numeric_range(self, value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> bool:
        """验证数值范围"""
        if not isinstance(value, (int, float)):
            raise ValidationError("值必须是数字")

        if value < min_val or value > max_val:
            raise ValidationError(f"值必须在 {min_val} 和 {max_val} 之间")

        return True

    def validate_list_items(self, items: List[Any], max_length: int = 100, item_validator = None) -> bool:
        """验证列表项"""
        if not isinstance(items, list):
            raise ValidationError("输入必须是列表")

        if len(items) > max_length:
            raise ValidationError(f"列表长度不能超过 {max_length}")

        if item_validator:
            for i, item in enumerate(items):
                try:
                    item_validator(item)
                except Exception as e:
                    raise ValidationError(f"第 {i+1} 项验证失败: {str(e)}")

        return True

    def validate_file_upload(self, file_data: Dict[str, Any], allowed_types: List[str], max_size: int) -> bool:
        """验证文件上传"""
        required_fields = ['filename', 'size', 'content_type']
        for field in required_fields:
            if field not in file_data:
                raise ValidationError(f"缺少文件字段: {field}")

        filename = file_data['filename']
        size = file_data['size']
        content_type = file_data['content_type']

        # 验证文件名
        if not isinstance(filename, str) or len(filename) == 0:
            raise ValidationError("文件名无效")

        # 验证文件大小
        if not isinstance(size, int) or size < 0:
            raise ValidationError("文件大小无效")

        if size > max_size:
            raise ValidationError(f"文件大小不能超过 {max_size} 字节")

        # 验证文件类型
        if not isinstance(content_type, str):
            raise ValidationError("文件类型无效")

        if content_type not in allowed_types:
            raise ValidationError(f"不支持的文件类型: {content_type}")

        # 验证文件扩展名
        allowed_extensions = self._get_allowed_extensions(allowed_types)
        file_extension = filename.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise ValidationError(f"不支持的文件扩展名: {file_extension}")

        return True

    def _get_allowed_extensions(self, allowed_types: List[str]) -> List[str]:
        """根据MIME类型获取允许的文件扩展名"""
        mime_to_extension = {
            'image/jpeg': ['jpg', 'jpeg'],
            'image/png': ['png'],
            'image/gif': ['gif'],
            'image/webp': ['webp'],
            'text/plain': ['txt'],
            'application/json': ['json'],
            'application/pdf': ['pdf']
        }

        extensions = []
        for mime_type in allowed_types:
            if mime_type in mime_to_extension:
                extensions.extend(mime_to_extension[mime_type])

        return list(set(extensions))

    def validate_business_rules(self, rule_name: str, data: Dict[str, Any]) -> bool:
        """验证业务规则"""
        validators = {
            'user_registration': self._validate_user_registration,
            'role_creation': self._validate_role_creation,
            'chat_session': self._validate_chat_session,
            'feedback_submission': self._validate_feedback_submission
        }

        validator = validators.get(rule_name)
        if not validator:
            raise ValidationError(f"未知的业务规则: {rule_name}")

        return validator(data)

    def _validate_user_registration(self, data: Dict[str, Any]) -> bool:
        """验证用户注册业务规则"""
        username = data.get('username', '')
        email = data.get('email', '')

        # 检查用户名是否已存在
        from ..models.user import User
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            raise ValidationError("用户名已存在")

        # 检查邮箱是否已存在
        existing_email = self.db.query(User).filter(User.email == email).first()
        if existing_email:
            raise ValidationError("邮箱已被注册")

        return True

    def _validate_role_creation(self, data: Dict[str, Any]) -> bool:
        """验证角色创建业务规则"""
        role_name = data.get('name', '')

        # 检查角色名称是否已存在
        from ..models.role import Role
        existing_role = self.db.query(Role).filter(Role.name == role_name).first()
        if existing_role:
            raise ValidationError("角色名称已存在")

        return True

    def _validate_chat_session(self, data: Dict[str, Any]) -> bool:
        """验证聊天会话业务规则"""
        user_id = data.get('user_id')
        role_id = data.get('role_id')

        # 检查用户是否存在
        from ..models.user import User
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValidationError("用户不存在")

        # 检查角色是否存在
        from ..models.role import Role
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValidationError("角色不存在")

        return True

    def _validate_feedback_submission(self, data: Dict[str, Any]) -> bool:
        """验证反馈提交业务规则"""
        user_id = data.get('user_id')
        role_id = data.get('role_id')

        # 检查用户和角色是否存在
        from ..models.user import User
        from ..models.role import Role

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValidationError("用户不存在")

        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValidationError("角色不存在")

        # 检查评分范围
        rating = data.get('rating')
        if rating is not None:
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                raise ValidationError("评分必须在1-5之间")

        return True

    def validate_sql_injection(self, input_string: str) -> bool:
        """检查SQL注入风险"""
        if not isinstance(input_string, str):
            return False

        # SQL注入关键词
        sql_keywords = [
            'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
            'UNION', 'JOIN', 'WHERE', 'OR', 'AND', 'LIKE', 'IN', 'BETWEEN',
            'HAVING', 'GROUP BY', 'ORDER BY', 'LIMIT', 'OFFSET', 'DISTINCT'
        ]

        # 转换为大写进行检查
        upper_input = input_string.upper()

        for keyword in sql_keywords:
            # 检查是否包含SQL关键词
            if keyword in upper_input:
                # 检查是否是独立的词汇（避免误判）
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, upper_input):
                    return False

        return True

    def validate_xss_attack(self, input_string: str) -> bool:
        """检查XSS攻击风险"""
        if not isinstance(input_string, str):
            return False

        # XSS攻击模式
        xss_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'onclick=',
            r'onmouseover=',
            r'onfocus=',
            r'onblur=',
            r'onchange=',
            r'onsubmit=',
            r'onreset=',
            r'onselect=',
            r'onunload=',
            r'data:',
            r'file:',
            r'ftp:',
            r'expression\(',
            r'eval\(',
            r'script\(',
            r'iframe',
            r'frame',
            r'object',
            r'embed',
            r'link',
            r'meta',
            r'base',
            r'applet',
            r'form'
        ]

        for pattern in xss_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return False

        return True

    def comprehensive_validation(self, data: Dict[str, Any], validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """综合验证"""
        errors = []

        for field, rules in validation_rules.items():
            field_value = data.get(field)

            # 检查必需字段
            if rules.get('required', False) and field_value is None:
                errors.append(f"字段 {field} 是必需的")
                continue

            # 如果字段为空且不是必需的，跳过验证
            if field_value is None:
                continue

            # 类型验证
            expected_type = rules.get('type')
            if expected_type and not isinstance(field_value, expected_type):
                errors.append(f"字段 {field} 类型错误，期望 {expected_type.__name__}")

            # 长度验证
            if 'min_length' in rules and len(str(field_value)) < rules['min_length']:
                errors.append(f"字段 {field} 长度不能少于 {rules['min_length']}")

            if 'max_length' in rules and len(str(field_value)) > rules['max_length']:
                errors.append(f"字段 {field} 长度不能超过 {rules['max_length']}")

            # 数值范围验证
            if 'min_value' in rules and field_value < rules['min_value']:
                errors.append(f"字段 {field} 不能小于 {rules['min_value']}")

            if 'max_value' in rules and field_value > rules['max_value']:
                errors.append(f"字段 {field} 不能大于 {rules['max_value']}")

            # 正则表达式验证
            if 'pattern' in rules:
                if not re.match(rules['pattern'], str(field_value)):
                    errors.append(f"字段 {field} 格式不正确")

            # 自定义验证器
            if 'validator' in rules:
                try:
                    rules['validator'](field_value)
                except Exception as e:
                    errors.append(f"字段 {field} 验证失败: {str(e)}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }