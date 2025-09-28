import os
import requests
import json
import base64
from typing import Optional


def transcribe_audio_real(audio_bytes: bytes) -> str:
    """
    使用真实STT API进行语音转文字
    支持百度、OpenAI等多种API

    Args:
        audio_bytes: 音频文件的二进制数据

    Returns:
        str: 转换后的文字内容
    """
    # 检查API配置优先级：百度 > OpenAI > 通用
    baidu_app_id = os.getenv('BAIDU_APP_ID')
    baidu_api_key = os.getenv('BAIDU_API_KEY')
    baidu_secret_key = os.getenv('BAIDU_SECRET_KEY')
    
    openai_key = os.getenv('OPENAI_API_KEY')
    stt_key = os.getenv('STT_API_KEY')
    
    if baidu_app_id and baidu_api_key and baidu_secret_key:
        # 使用百度语音识别API
        return transcribe_audio_baidu(audio_bytes, baidu_app_id, baidu_api_key, baidu_secret_key)
    elif openai_key or stt_key:
        # 使用OpenAI API
        return transcribe_audio_openai(audio_bytes, openai_key or stt_key)
    else:
        raise ValueError("未配置STT API密钥，请设置百度或OpenAI API密钥")


def transcribe_audio_baidu(audio_bytes: bytes, app_id: str, api_key: str, secret_key: str) -> str:
    """
    使用百度语音识别API进行语音转文字
    
    Args:
        audio_bytes: 音频文件的二进制数据
        app_id: 百度应用ID
        api_key: 百度API Key
        secret_key: 百度Secret Key
    
    Returns:
        str: 转换后的文字内容
    """
    try:
        # 将音频转换为base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # 百度语音识别API URL
        url = "https://vop.baidu.com/server_api"
        
        # 构建请求数据
        data = {
            "format": "wav",
            "rate": 16000,
            "channel": 1,
            "cuid": "ai_roleplay",
            "token": get_baidu_access_token(api_key, secret_key),
            "speech": audio_base64,
            "len": len(audio_bytes)
        }
        
        # 发送请求
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('err_no') == 0:
            return ''.join(result.get('result', []))
        else:
            raise Exception(f"百度语音识别失败: {result.get('err_msg', '未知错误')}")
            
    except Exception as e:
        print(f"[STT] 百度API调用失败: {e}")
        raise Exception(f"百度语音识别失败: {e}")


def get_baidu_access_token(api_key: str, secret_key: str) -> str:
    """
    获取百度API访问令牌
    
    Args:
        api_key: 百度API Key
        secret_key: 百度Secret Key
    
    Returns:
        str: 访问令牌
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    
    response = requests.post(url, params=params, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    return result.get('access_token')


def transcribe_audio_openai(audio_bytes: bytes, api_key: str) -> str:
    """
    使用OpenAI API进行语音转文字
    
    Args:
        audio_bytes: 音频文件的二进制数据
        api_key: OpenAI API Key
    
    Returns:
        str: 转换后的文字内容
    """
    try:
        api_url = os.getenv('STT_API_URL', 'https://api.openai.com/v1/audio/transcriptions')
        
        # 准备文件上传
        files = {
            'file': ('audio.wav', audio_bytes, 'audio/wav'),
            'model': (None, 'whisper-1')
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        # 发送请求
        response = requests.post(api_url, files=files, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get('text', '')
        
    except Exception as e:
        print(f"[STT] OpenAI API调用失败: {e}")
        raise Exception(f"OpenAI语音识别失败: {e}")


# 模拟函数已删除，直接使用真实STT API


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    语音转文字（直接使用真实STT API）
    
    Args:
        audio_bytes: 音频文件的二进制数据
    
    Returns:
        str: 转换后的文字内容
    """
    # 直接使用真实STT API
    return transcribe_audio_real(audio_bytes)
