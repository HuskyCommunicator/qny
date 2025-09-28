"""
语音合成服务 - 支持真实TTS API和模拟服务
集成阿里云语音合成服务，支持多种语音和音色
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from app.core.config import settings


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


def synthesize_speech_real(text: str, voice: str = "longxiaochun", format: str = "mp3", rate: int = 16000) -> Optional[bytes]:
    """
    使用真实TTS API生成语音
    支持百度、阿里云等多种API

    Args:
        text: 要合成的文本
        voice: 发音人，默认为"longxiaochun"（龙小春）
        format: 音频格式，默认为"mp3"
        rate: 采样率，默认为16000

    Returns:
        音频数据(bytes)或None(失败时)
    """
    try:
        # 检查API配置优先级：百度 > 阿里云 > OpenAI
        baidu_app_id = os.getenv('BAIDU_APP_ID')
        baidu_api_key = os.getenv('BAIDU_API_KEY')
        baidu_secret_key = os.getenv('BAIDU_SECRET_KEY')
        
        dashscope_key = settings.dashscope_api_key or os.getenv("DASHSCOPE_API_KEY")
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if baidu_app_id and baidu_api_key and baidu_secret_key:
            # 使用百度语音合成API
            return synthesize_speech_baidu(text, voice, format, rate, baidu_app_id, baidu_api_key, baidu_secret_key)
        elif dashscope_key:
            # 使用阿里云语音合成API
            return synthesize_speech_dashscope(text, voice, format, rate, dashscope_key)
        elif openai_key:
            # 使用OpenAI API
            return synthesize_speech_openai(text, voice, format, rate, openai_key)
        else:
            raise ValueError("未配置TTS API密钥，请设置百度、阿里云或OpenAI API密钥")

        # 阿里云语音合成API URL
        url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts"

        # 构建请求头
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 构建请求体
        payload = {
            "model": "sambert-zhide-v1",  # 智臻音色模型
            "input": {
                "text": text
            },
            "parameters": {
                "voice": voice,
                "format": format,
                "rate": rate,
                "volume": 50,  # 音量 0-100
                "pitch": 0,    # 音调 -20到20
                "enable_phoneme_timestamp": False
            }
        }

        print(f"[TTS] 请求阿里云语音合成服务: text='{text[:50]}...', voice={voice}")

        # 发送请求
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            # 检查响应类型
            content_type = response.headers.get('content-type', '')
            if 'audio' in content_type or 'application/octet-stream' in content_type:
                print(f"[TTS] 语音合成成功，音频大小: {len(response.content)} bytes")
                return response.content
            else:
                # 可能返回错误信息
                try:
                    error_data = response.json()
                    print(f"[TTS] 语音合成失败: {error_data}")
                except:
                    print(f"[TTS] 语音合成失败: 非音频响应 {content_type}")
                return None
        else:
            print(f"[TTS] 语音合成失败: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"[TTS] 错误详情: {error_data}")
            except:
                print(f"[TTS] 错误响应: {response.text}")
            return None

    except requests.RequestException as e:
        print(f"[TTS] 网络请求异常: {e}")
        return None
    except Exception as e:
        print(f"[TTS] 语音合成异常: {e}")
        return None


# 模拟函数已删除，直接使用真实TTS API


def synthesize_speech(
    text: str,
    voice: str = "longxiaochun",
    format: str = "mp3",
    rate: int = 16000
) -> bytes:
    """
    语音合成主函数 - 直接使用真实TTS API

    Args:
        text: 要合成的文本
        voice: 发音人，默认为"longxiaochun"
        format: 音频格式，默认为"mp3"
        rate: 采样率，默认为16000

    Returns:
        音频数据

    支持的发音人:
    - longxiaochun: 龙小春 (温暖女声)
    - longxiaochun_emotional: 龙小春 (情感女声)
    - longfei: 龙飞 (成熟男声)
    - longxiaowen: 龙小雯 (温柔女声)
    - longjing: 龙静 (知性女声)
    """
    # 直接使用真实TTS服务
    return synthesize_speech_real(text, voice, format, rate)


def get_available_voices() -> Dict[str, Dict[str, Any]]:
    """
    获取可用的发音人列表

    Returns:
        发音人信息字典
    """
    return {
        "longxiaochun": {
            "name": "龙小春",
            "gender": "女",
            "style": "温暖亲切",
            "description": "适合日常对话、故事讲述"
        },
        "longxiaochun_emotional": {
            "name": "龙小春(情感)",
            "gender": "女",
            "style": "情感丰富",
            "description": "适合表达丰富情感的对话"
        },
        "longfei": {
            "name": "龙飞",
            "gender": "男",
            "style": "成熟稳重",
            "description": "适合正式场合、商务对话"
        },
        "longxiaowen": {
            "name": "龙小雯",
            "gender": "女",
            "style": "温柔甜美",
            "description": "适合温柔安慰、情感支持"
        },
        "longjing": {
            "name": "龙静",
            "gender": "女",
            "style": "知性优雅",
            "description": "适合知识讲解、专业内容"
        }
    }


def synthesize_speech_baidu(text: str, voice: str, format: str, rate: int, app_id: str, api_key: str, secret_key: str) -> bytes:
    """使用百度语音合成API生成语音"""
    try:
        url = "https://tsn.baidu.com/text2audio"
        token = get_baidu_access_token(api_key, secret_key)
        
        params = {
            "tex": text,
            "tok": token,
            "cuid": "ai_roleplay",
            "ctp": 1,
            "lan": "zh",
            "spd": 5,
            "pit": 5,
            "vol": 5,
            "per": get_baidu_voice_id(voice),
            "aue": 3 if format == "mp3" else 4
        }
        
        response = requests.post(url, params=params, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if 'audio' in content_type:
            return response.content
        else:
            raise Exception(f"百度语音合成失败: {response.text}")
            
    except Exception as e:
        print(f"[TTS] 百度API调用失败: {e}")
        raise Exception(f"百度语音合成失败: {e}")


def get_baidu_voice_id(voice: str) -> int:
    """获取百度语音合成发音人ID"""
    voice_mapping = {
        "longxiaochun": 0,  # 度小美
        "longxiaochun_emotional": 1,  # 度小宇
        "longfei": 3,  # 度逍遥
        "longxiaowen": 4,  # 度小娇
        "longjing": 5,  # 度小萌
    }
    return voice_mapping.get(voice, 0)


def synthesize_speech_dashscope(text: str, voice: str, format: str, rate: int, api_key: str) -> bytes:
    """使用阿里云语音合成API生成语音"""
    try:
        url = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        data = {
            "model": "sambert-zhichang-v1",
            "input": {"text": text},
            "parameters": {"voice": voice, "format": format, "sample_rate": rate}
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get("output", {}).get("audio"):
            import base64
            return base64.b64decode(result["output"]["audio"])
        else:
            raise Exception(f"阿里云语音合成失败: {result.get('message', '未知错误')}")
            
    except Exception as e:
        print(f"[TTS] 阿里云API调用失败: {e}")
        raise Exception(f"阿里云语音合成失败: {e}")


def synthesize_speech_openai(text: str, voice: str, format: str, rate: int, api_key: str) -> bytes:
    """使用OpenAI API生成语音"""
    try:
        url = "https://api.openai.com/v1/audio/speech"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        data = {
            "model": "tts-1",
            "input": text,
            "voice": voice,
            "response_format": format
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        return response.content
        
    except Exception as e:
        print(f"[TTS] OpenAI API调用失败: {e}")
        raise Exception(f"OpenAI语音合成失败: {e}")


