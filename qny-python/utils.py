import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# AI服务配置
API_KEY = os.getenv("API_KEY", "")
PROVIDER = os.getenv("PROVIDER", "openai")

def call_ai_service(user_message: str, system_prompt: str, agent_name: str) -> str:
    """
    调用AI服务生成回复
    """
    try:
        if PROVIDER.lower() == "openai":
            return _call_openai(user_message, system_prompt, agent_name)
        else:
            # 可以添加其他AI提供商
            return _call_openai(user_message, system_prompt, agent_name)
    except Exception as e:
        print(f"AI服务调用失败: {e}")
        return f"抱歉，{agent_name}暂时无法回复，请稍后再试。"

def _call_openai(user_message: str, system_prompt: str, agent_name: str) -> str:
    """
    调用OpenAI API
    """
    if not API_KEY:
        return f"你好！我是{agent_name}。由于API配置问题，我暂时无法提供完整的回复功能。请检查API密钥配置。"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 构建对话历史
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    data = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"OpenAI API错误: {response.status_code} - {response.text}")
            return f"抱歉，{agent_name}正在休息中，请稍后再试。"

    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return f"网络连接问题，{agent_name}暂时无法回复。"

def generate_session_title(first_message: str) -> str:
    """
    根据第一条消息生成会话标题
    """
    if len(first_message) <= 20:
        return first_message
    else:
        return first_message[:20] + "..."