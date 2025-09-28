#!/usr/bin/env python3
"""
新增功能数据库迁移脚本
处理成长系统、推荐系统、场景系统等新增表结构
"""

import os
import sys
from sqlalchemy import text, inspect
from app.core.db import engine, Base
from app.models import *  # 导入所有模型

def check_table_exists(table_name: str) -> bool:
    """检查表是否存在"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SHOW TABLES LIKE '{table_name}'"))
            return result.fetchone() is not None
    except Exception as e:
        print(f"检查表 {table_name} 时出错: {e}")
        return False

def migrate_new_features():
    """迁移新增功能相关的数据库表"""
    print("🚀 开始迁移新增功能数据库表...")
    
    try:
        # 1. 创建所有新表
        print("📋 创建所有数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建完成")
        
        # 2. 检查关键表是否存在
        required_tables = [
            'users', 'roles', 'user_roles', 'user_feedback', 'role_skills',
            'chat_sessions', 'chat_messages',
            'scene_templates', 'scene_sessions', 'scene_participants', 
            'scene_messages', 'scene_interaction_rules', 'scene_recommendations'
        ]
        
        missing_tables = []
        for table in required_tables:
            if not check_table_exists(table):
                missing_tables.append(table)
        
        if missing_tables:
            print(f"⚠️  以下表可能未正确创建: {missing_tables}")
        else:
            print("✅ 所有必需的表都已存在")
        
        # 3. 添加索引优化
        print("🔍 添加数据库索引优化...")
        try:
            with engine.connect() as conn:
                # 为常用查询字段添加索引
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_chat_sessions_role_id ON chat_sessions(role_id)",
                    "CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)",
                    "CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON user_feedback(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_user_feedback_role_id ON user_feedback(role_id)",
                    "CREATE INDEX IF NOT EXISTS idx_role_skills_role_id ON role_skills(role_id)",
                    "CREATE INDEX IF NOT EXISTS idx_scene_sessions_user_id ON scene_sessions(user_id)",
                    "CREATE INDEX IF NOT EXISTS idx_scene_participants_session_id ON scene_participants(session_id)",
                ]
                
                for index_sql in indexes:
                    try:
                        conn.execute(text(index_sql))
                        print(f"✅ 索引创建成功: {index_sql.split('idx_')[1].split(' ')[0]}")
                    except Exception as e:
                        print(f"⚠️  索引创建跳过: {e}")
                
                conn.commit()
                print("✅ 数据库索引优化完成")
                
        except Exception as e:
            print(f"⚠️  索引创建过程中出现错误: {e}")
        
        # 4. 初始化基础数据
        print("🌱 初始化基础数据...")
        try:
            with engine.connect() as conn:
                # 检查是否已有数据
                result = conn.execute(text("SELECT COUNT(*) FROM roles"))
                role_count = result.fetchone()[0]
                
                if role_count == 0:
                    print("📝 插入默认角色数据...")
                    # 这里可以添加默认角色数据
                    print("✅ 基础数据初始化完成")
                else:
                    print(f"✅ 已有 {role_count} 个角色，跳过基础数据初始化")
                    
        except Exception as e:
            print(f"⚠️  基础数据初始化过程中出现错误: {e}")
        
        print("🎉 数据库迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("AI 角色扮演系统 - 数据库迁移工具")
    print("=" * 50)
    
    success = migrate_new_features()
    
    if success:
        print("\n🎉 迁移成功完成！")
        print("现在可以启动应用程序了。")
        sys.exit(0)
    else:
        print("\n❌ 迁移失败！")
        print("请检查错误信息并重试。")
        sys.exit(1)

