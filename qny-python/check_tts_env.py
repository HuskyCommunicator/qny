#!/usr/bin/env python3
"""
检查TTS环境变量配置
"""

import os

def check_tts_env():
    """检查TTS环境变量配置"""
    print("🔍 检查TTS环境变量配置")
    print("=" * 40)
    
    # 检查百度API配置
    baidu_app_id = os.getenv('BAIDU_APP_ID')
    baidu_api_key = os.getenv('BAIDU_API_KEY')
    baidu_secret_key = os.getenv('BAIDU_SECRET_KEY')
    
    print("百度API配置:")
    print(f"  BAIDU_APP_ID: {'✅ 已配置' if baidu_app_id else '❌ 未配置'}")
    print(f"  BAIDU_API_KEY: {'✅ 已配置' if baidu_api_key else '❌ 未配置'}")
    print(f"  BAIDU_SECRET_KEY: {'✅ 已配置' if baidu_secret_key else '❌ 未配置'}")
    
    # 检查阿里云API配置
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    print(f"\n阿里云API配置:")
    print(f"  DASHSCOPE_API_KEY: {'✅ 已配置' if dashscope_key else '❌ 未配置'}")
    
    # 检查OpenAI API配置
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"\nOpenAI API配置:")
    print(f"  OPENAI_API_KEY: {'✅ 已配置' if openai_key else '❌ 未配置'}")
    
    # 确定优先级
    print(f"\nAPI优先级:")
    if baidu_app_id and baidu_api_key and baidu_secret_key:
        print("  1. 百度API (已配置)")
    else:
        print("  1. 百度API (未配置)")
        
    if dashscope_key:
        print("  2. 阿里云API (已配置)")
    else:
        print("  2. 阿里云API (未配置)")
        
    if openai_key:
        print("  3. OpenAI API (已配置)")
    else:
        print("  3. OpenAI API (未配置)")
    
    # 推荐配置
    if not any([baidu_app_id and baidu_api_key and baidu_secret_key, dashscope_key, openai_key]):
        print("\n⚠️  警告: 未配置任何TTS API密钥")
        print("请至少配置以下之一:")
        print("  - 百度API: BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY")
        print("  - 阿里云API: DASHSCOPE_API_KEY")
        print("  - OpenAI API: OPENAI_API_KEY")

if __name__ == "__main__":
    check_tts_env()



