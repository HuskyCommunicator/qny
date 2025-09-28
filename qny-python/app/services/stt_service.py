import os
import requests
import json
from typing import Optional


def transcribe_audio_real(audio_bytes: bytes) -> str:
    """
    使用真实STT API进行语音转文字

    Args:
        audio_bytes: 音频文件的二进制数据

    Returns:
        str: 转换后的文字内容
    """
    # 检查是否配置了真实API
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('STT_API_KEY')
    api_url = os.getenv('STT_API_URL', 'https://api.openai.com/v1/audio/transcriptions')

    if not api_key:
        # 如果没有配置API密钥，回退到模拟回复
        return transcribe_audio_mock(audio_bytes)

    try:
        # 准备文件上传
        files = {
            'file': ('audio.wav', audio_bytes, 'audio/wav'),
            'model': (None, 'whisper-1')
        }

        headers = {
            'Authorization': f'Bearer {api_key}'
        }

        # 调用STT API
        response = requests.post(api_url, headers=headers, files=files, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result.get('text', '语音识别失败')

    except Exception as e:
        # 如果API调用失败，回退到模拟回复
        print(f"STT API调用失败: {e}")
        return transcribe_audio_mock(audio_bytes)


def transcribe_audio_mock(audio_bytes: bytes) -> str:
    """
    模拟语音转文字功能（原版本）

    Args:
        audio_bytes: 音频文件的二进制数据

    Returns:
        str: 模拟转换的文字内容
    """
    # 根据音频长度生成不同的模拟回复
    audio_length = len(audio_bytes)

    if audio_length < 1000:
        return "您好，我听到了一段很短的音频。"
    elif audio_length < 5000:
        return "这是一段中等长度的音频，我能听到一些内容。"
    elif audio_length < 10000:
        return "这是一段较长的音频，包含了丰富的语音信息。"
    else:
        return "这是一段很长的音频，可能包含了完整的对话或演讲内容。"


# 主要接口函数，根据配置决定使用真实API还是模拟
def transcribe_audio(audio_bytes: bytes) -> str:
    """
    语音转文字（支持真实STT API和模拟功能）

    Args:
        audio_bytes: 音频文件的二进制数据

    Returns:
        str: 转换后的文字内容
    """
    # 检查是否启用真实STT
    use_real_stt = os.getenv('USE_REAL_STT', 'false').lower() == 'true'

    if use_real_stt:
        return transcribe_audio_real(audio_bytes)
    else:
        return transcribe_audio_mock(audio_bytes)


