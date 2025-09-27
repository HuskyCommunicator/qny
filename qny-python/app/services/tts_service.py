"""
语音合成服务 - 支持真实TTS API和模拟服务
集成阿里云语音合成服务，支持多种语音和音色
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from app.core.config import settings


def synthesize_speech_real(text: str, voice: str = "longxiaochun", format: str = "mp3", rate: int = 16000) -> Optional[bytes]:
    """
    使用阿里云语音合成服务生成语音

    Args:
        text: 要合成的文本
        voice: 发音人，默认为"longxiaochun"（龙小春）
        format: 音频格式，默认为"mp3"
        rate: 采样率，默认为16000

    Returns:
        音频数据(bytes)或None(失败时)
    """
    try:
        # 检查是否启用真实TTS服务
        if not settings.use_real_tts:
            return None

        # 获取阿里云API密钥
        api_key = settings.dashscope_api_key or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print(f"[TTS] 阿里云API密钥未配置，使用模拟服务")
            return None

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


def synthesize_speech_mock(text: str, voice: str = "default", format: str = "mp3") -> bytes:
    """
    模拟语音合成服务 - 用于测试和开发

    Args:
        text: 要合成的文本
        voice: 发音人（仅用于模拟）
        format: 音频格式（仅用于模拟）

    Returns:
        模拟的音频数据
    """
    # 生成模拟音频数据
    audio_data = f"AUDIO({text})-VOICE({voice})-FORMAT({format})".encode("utf-8")

    print(f"[TTS Mock] 模拟语音合成: text='{text[:50]}...', voice={voice}")

    return audio_data


def synthesize_speech(
    text: str,
    voice: str = "longxiaochun",
    format: str = "mp3",
    rate: int = 16000,
    force_mock: bool = False
) -> bytes:
    """
    语音合成主函数 - 自动选择真实API或模拟服务

    Args:
        text: 要合成的文本
        voice: 发音人，默认为"longxiaochun"
        format: 音频格式，默认为"mp3"
        rate: 采样率，默认为16000
        force_mock: 强制使用模拟服务

    Returns:
        音频数据

    支持的发音人:
    - longxiaochun: 龙小春 (温暖女声)
    - longxiaochun_emotional: 龙小春 (情感女声)
    - longfei: 龙飞 (成熟男声)
    - longxiaowen: 龙小雯 (温柔女声)
    - longjing: 龙静 (知性女声)
    """
    if force_mock or not settings.use_real_tts:
        # 使用模拟服务
        return synthesize_speech_mock(text, voice, format)
    else:
        # 尝试使用真实TTS服务
        result = synthesize_speech_real(text, voice, format, rate)
        if result is not None:
            return result
        else:
            # 真实服务失败，降级到模拟服务
            print(f"[TTS] 真实服务失败，降级到模拟服务")
            return synthesize_speech_mock(text, voice, format)


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


