#!/usr/bin/env python3
"""
快速语音功能测试脚本
验证登录和基本功能
"""

import requests
import json

def quick_test():
    """快速测试登录和基本功能"""
    base_url = "http://116.62.231.58:8000"
    
    print("🎤 快速语音功能测试")
    print("=" * 40)
    
    # 1. 测试登录
    print("1. 测试登录...")
    login_url = f"{base_url}/auth/login"
    login_data = {
        "username": "zhaoyunyun",
        "password": "123456qwe"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print(f"✅ 登录成功，Token: {token[:20]}...")
            
            # 设置请求头
            headers = {"Authorization": f"Bearer {token}"}
            
            # 2. 测试TTS
            print("\n2. 测试TTS...")
            tts_url = f"{base_url}/chat/tts"
            tts_data = {
                "content": "你好，这是语音合成测试",
                "voice": "longxiaochun",
                "format": "mp3"
            }
            
            tts_response = requests.post(tts_url, json=tts_data, headers=headers)
            if tts_response.status_code == 200:
                result = tts_response.json()
                audio_base64 = result.get("audio_base64")
                if audio_base64:
                    print("✅ TTS测试成功，返回音频数据")
                else:
                    print("❌ TTS测试失败，无音频数据")
            else:
                print(f"❌ TTS测试失败: {tts_response.text}")
            
            # 3. 测试聊天
            print("\n3. 测试聊天...")
            chat_url = f"{base_url}/chat/text"
            chat_data = {
                "content": "你好",
                "role_id": 1
            }
            
            chat_response = requests.post(chat_url, json=chat_data, headers=headers)
            if chat_response.status_code == 200:
                result = chat_response.json()
                reply = result.get("content")
                print(f"✅ 聊天测试成功，AI回复: {reply[:30]}...")
            else:
                print(f"❌ 聊天测试失败: {chat_response.text}")
            
            print("\n🎉 快速测试完成！")
            return True
            
        else:
            print(f"❌ 登录失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败！")
