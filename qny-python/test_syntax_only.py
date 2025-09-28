#!/usr/bin/env python3
"""
语法检查脚本
只检查Python语法，不依赖外部库
"""

import ast
import os
import sys

def check_syntax(file_path):
    """检查Python文件的语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析AST
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误: {e}"
    except Exception as e:
        return False, f"其他错误: {e}"

def test_syntax():
    """测试所有Python文件的语法"""
    print("🔍 检查Python文件语法...")
    
    # 要检查的文件列表
    files_to_check = [
        "main.py",
        "app/models/role.py",
        "app/models/user.py", 
        "app/models/chat.py",
        "app/models/scene.py",
        "app/schemas/role.py",
        "app/schemas/chat.py",
        "app/schemas/user.py",
        "app/schemas/growth.py",
        "app/schemas/recommendation.py",
        "app/schemas/scene.py",
        "app/routers/role.py",
        "app/routers/chat.py",
        "app/routers/auth.py",
        "app/routers/me.py",
        "app/routers/growth.py",
        "app/routers/recommendation.py",
        "app/routers/scene.py",
        "app/services/chat_service.py",
        "app/services/growth_service.py",
        "app/services/recommendation_service.py",
        "app/services/scene_service.py",
        "app/core/config.py",
        "app/core/db.py",
        "app/core/security.py",
        "app/core/exceptions.py",
        "app/core/response.py",
        "app/core/constants.py",
        "app/core/middleware.py",
        "prompt_templates.py"
    ]
    
    success_count = 0
    total_count = 0
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            total_count += 1
            print(f"检查 {file_path}...", end=" ")
            success, error = check_syntax(file_path)
            if success:
                print("✅")
                success_count += 1
            else:
                print(f"❌ {error}")
        else:
            print(f"⚠️  {file_path} 不存在")
    
    print(f"\n📊 语法检查结果: {success_count}/{total_count} 个文件通过")
    return success_count == total_count

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 AI角色扮演系统 - 语法检查")
    print("=" * 60)
    
    success = test_syntax()
    
    if success:
        print("\n✅ 所有文件语法检查通过！")
        print("代码结构是正确的，可以继续开发。")
    else:
        print("\n❌ 部分文件语法检查失败！")
        print("请修复语法错误后重试。")
        exit(1)

