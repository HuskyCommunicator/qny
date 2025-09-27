#!/usr/bin/env python3

"""
数据库初始化脚本
用于创建新的数据库表结构
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.core.config import settings
from app.core.db import Base
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.chat import ChatSession, ChatMessage

def create_tables():
    """创建所有数据库表"""
    print("正在创建数据库表...")

    engine = create_engine(settings.database_url)

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    print("数据库表创建成功！")
    print("创建的表包括：")
    print("- users: 用户表")
    print("- roles: 角色表")
    print("- user_roles: 用户角色关联表")
    print("- chat_sessions: 聊天会话表")
    print("- chat_messages: 聊天消息表")

if __name__ == "__main__":
    create_tables()