"""
数据库初始化脚本
用于创建预设的角色数据
"""

from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models import Role, User
from prompt_templates import ROLE_TEMPLATES


def init_template_roles():
    """从模板初始化预设角色"""
    db = SessionLocal()

    try:
        # 检查是否已经有管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("警告: 未找到管理员用户，跳过模板角色初始化")
            return

        print(f"开始初始化角色模板，创建者: {admin_user.username}")

        for template_key, template in ROLE_TEMPLATES.items():
            # 检查角色是否已存在
            existing_role = db.query(Role).filter(Role.name == template.name).first()

            if existing_role:
                print(f"角色 '{template.name}' 已存在，跳过")
                continue

            # 创建角色
            role = Role(
                name=template.name,
                description=template.description,
                system_prompt=template.system_prompt,
                avatar_url=template.avatar_url,
                is_public=True,
                is_active=True,
                created_by=admin_user.id,
                config=template.config,
                tags=template.tags,
                category=template.category
            )

            db.add(role)
            print(f"创建角色: {template.name}")

        db.commit()
        print("角色模板初始化完成")

    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
    finally:
        db.close()


def create_admin_user():
    """创建管理员用户"""
    db = SessionLocal()

    try:
        # 检查管理员用户是否已存在
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("管理员用户已存在")
            return

        from app.core.security import get_password_hash

        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="系统管理员",
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        print("管理员用户创建成功")

    except Exception as e:
        db.rollback()
        print(f"创建管理员用户失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("开始初始化数据库...")

    # 创建管理员用户
    create_admin_user()

    # 初始化角色模板
    init_template_roles()

    print("数据库初始化完成")