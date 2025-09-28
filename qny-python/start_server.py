#!/usr/bin/env python3
"""
🤖 AI角色扮演系统 - 启动工具
检查环境、运行迁移、启动服务器
"""

import os
import sys
import subprocess
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """检查Python版本"""
    version = sys.version
    logger.info(f"✅ Python版本: {version}")
    return True

def run_database_migration():
    """运行数据库迁移"""
    logger.info("🔄 运行数据库迁移...")
    
    try:
        # 尝试运行迁移脚本
        result = subprocess.run([sys.executable, "migrate_new_features.py"], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✅ 数据库迁移成功")
            return True
        else:
            logger.error(f"❌ 数据库迁移失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ 数据库迁移超时")
        return False
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        return False

def start_uvicorn_server():
    """启动uvicorn服务器"""
    logger.info("🚀 启动服务器...")
    
    try:
        # 启动uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ]
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        logger.info("🛑 服务器已停止")
    except Exception as e:
        logger.error(f"❌ 启动服务器失败: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("🤖 AI角色扮演系统 - 启动工具")
    print("=" * 60)
    
    # 1. 检查Python版本
    if not check_python_version():
        logger.error("❌ Python版本检查失败")
        return 1
    
    # 2. 运行数据库迁移
    if not run_database_migration():
        logger.error("❌ 数据库迁移失败，无法启动服务器")
        return 1
    
    # 3. 启动服务器
    logger.info("✅ 准备启动服务器...")
    if not start_uvicorn_server():
        logger.error("❌ 服务器启动失败")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
