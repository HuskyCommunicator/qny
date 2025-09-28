from typing import List, Dict, Optional
import os
import time
import requests
from sqlalchemy.orm import Session
from ..core.config import settings
from ..models.role import Role
from ..services.rag_service import rag


def get_llm_config():
    """
    获取LLM配置的统一函数
    返回: (api_key, api_url, model, use_rag)
    """
    # 直接使用真实LLM，不再检查开关
    use_rag = os.getenv('USE_RAG', 'true').lower() == 'true'
    
    # 获取API密钥（优先级：DASHSCOPE_API_KEY > OPENAI_API_KEY > LLM_API_KEY）
    api_key = (
        os.getenv('DASHSCOPE_API_KEY') or 
        os.getenv('OPENAI_API_KEY') or 
        os.getenv('LLM_API_KEY')
    )
    
    # 根据API密钥类型确定URL和模型
    if os.getenv('DASHSCOPE_API_KEY'):
        # 使用通义千问
        api_url = os.getenv('LLM_API_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions')
        model = os.getenv('LLM_MODEL', 'qwen-plus')
    elif os.getenv('OPENAI_API_KEY'):
        # 使用OpenAI
        api_url = os.getenv('LLM_API_URL', 'https://api.openai.com/v1/chat/completions')
        model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    else:
        # 使用通用LLM API
        api_url = os.getenv('LLM_API_URL', 'https://api.openai.com/v1/chat/completions')
        model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    
    return api_key, api_url, model, use_rag


def generate_reply_with_rag(messages: List[Dict[str, str]], role_id: Optional[int] = None, db: Session = None) -> str:
    """
    使用RAG增强的LLM生成回复
    
    Args:
        messages: 聊天历史记录
        role_id: 角色ID
        db: 数据库会话
    
    Returns:
        str: AI回复内容
    """
    # RAG检索相关文档
    relevant_docs = []
    try:
        if messages:
            last_message = messages[-1].get('content', '')
            relevant_docs = rag.search(last_message, top_k=3)
            print(f"[RAG] 检索到 {len(relevant_docs)} 个相关文档")
    except Exception as e:
        print(f"[RAG] 检索失败: {e}")
    
    # 获取LLM配置
    api_key, api_url, model, use_rag = get_llm_config()
    
    # 如果没有配置API密钥，抛出异常
    if not api_key:
        raise ValueError("未配置LLM API密钥，请设置DASHSCOPE_API_KEY、OPENAI_API_KEY或LLM_API_KEY")
    
    try:
        # 构建消息列表
        api_messages = []
        
        # 添加角色系统提示
        if role_id and db:
            try:
                role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
                if role and role.system_prompt:
                    # 添加角色系统提示
                    api_messages.append({
                        "role": "system",
                        "content": role.system_prompt
                    })
            except Exception as e:
                print(f"获取角色信息失败: {e}")
        
        # 如果没有角色系统提示，使用默认提示
        if not api_messages:
            default_prompt = "你是一个智能助手，请根据用户的提问提供有帮助的回答。"
            # 如果有RAG检索结果，构建增强的上下文
            if relevant_docs:
                default_prompt = build_rag_context(relevant_docs, default_prompt)
            api_messages.append({
                "role": "system",
                "content": default_prompt
            })
        
        # 添加用户消息
        for msg in messages:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # 调用LLM API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": api_messages,
            "max_tokens": 800,  # 减少token数量以提高响应速度
            "temperature": 0.7,
            "stream": False  # 确保不使用流式响应
        }
        
        # 添加重试机制
        for attempt in range(settings.llm_max_retries):
            try:
                response = requests.post(api_url, headers=headers, json=data, timeout=settings.llm_timeout_sec)
                response.raise_for_status()
                
                result = response.json()
                return result['choices'][0]['message']['content']
                
            except requests.exceptions.Timeout:
                print(f"[RAG] LLM API超时 (尝试 {attempt + 1}/{settings.llm_max_retries}): {settings.llm_timeout_sec}s")
                if attempt == settings.llm_max_retries - 1:
                    raise
                time.sleep(1)  # 等待1秒后重试
            except requests.exceptions.RequestException as e:
                print(f"[RAG] LLM API请求失败 (尝试 {attempt + 1}/{settings.llm_max_retries}): {e}")
                if attempt == settings.llm_max_retries - 1:
                    raise
                time.sleep(1)  # 等待1秒后重试
        
    except Exception as e:
        # 如果API调用失败，抛出异常
        print(f"[RAG] LLM API调用失败: {e}")
        raise Exception(f"LLM API调用失败: {e}")


def build_rag_context(relevant_docs: List[tuple], base_prompt: str = "") -> str:
    """
    构建包含RAG检索信息的上下文
    
    Args:
        relevant_docs: RAG检索结果列表 [(doc_id, content, score), ...]
        base_prompt: 基础系统提示
    
    Returns:
        str: 增强后的系统提示
    """
    if not relevant_docs:
        return base_prompt
    
    context_parts = [base_prompt]
    context_parts.append("\n\n相关背景知识：")
    
    for i, (doc_id, content, score) in enumerate(relevant_docs, 1):
        context_parts.append(f"\n{i}. {content[:200]}...")
    
    context_parts.append("\n\n请结合以上背景知识回答用户的问题。")
    
    return "".join(context_parts)


def generate_reply_real_llm(messages: List[Dict[str, str]], role_id: Optional[int] = None, db: Session = None) -> str:
    """
    使用真实LLM API生成回复（不包含RAG）
    
    Args:
        messages: 聊天历史记录
        role_id: 角色ID
        db: 数据库会话
    
    Returns:
        str: AI回复内容
    """
    # 获取LLM配置
    api_key, api_url, model, use_rag = get_llm_config()

    # 如果没有配置API密钥，抛出异常
    if not api_key:
        raise ValueError("未配置LLM API密钥，请设置DASHSCOPE_API_KEY、OPENAI_API_KEY或LLM_API_KEY")

    try:
        # 构建消息列表
        api_messages = []

        # 添加角色系统提示
        if role_id and db:
            try:
                role = db.query(Role).filter(Role.id == role_id, Role.is_active == True).first()
                if role and role.system_prompt:
                    # 添加角色系统提示
                    api_messages.append({
                        "role": "system",
                        "content": role.system_prompt
                    })
            except Exception as e:
                print(f"获取角色信息失败: {e}")

        # 如果没有角色系统提示，使用默认提示
        if not api_messages:
            api_messages.append({
                "role": "system",
                "content": "你是一个智能助手，请根据用户的提问提供有帮助的回答。"
            })

        # 添加用户消息
        for msg in messages:
            api_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 调用LLM API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": api_messages,
            "max_tokens": 800,  # 减少token数量以提高响应速度
            "temperature": 0.7,
            "stream": False  # 确保不使用流式响应
        }

        # 添加重试机制
        for attempt in range(settings.llm_max_retries):
            try:
                response = requests.post(api_url, headers=headers, json=data, timeout=settings.llm_timeout_sec)
                response.raise_for_status()
                
                result = response.json()
                return result['choices'][0]['message']['content']
                
            except requests.exceptions.Timeout:
                print(f"LLM API超时 (尝试 {attempt + 1}/{settings.llm_max_retries}): {settings.llm_timeout_sec}s")
                if attempt == settings.llm_max_retries - 1:
                    raise
                time.sleep(1)  # 等待1秒后重试
            except requests.exceptions.RequestException as e:
                print(f"LLM API请求失败 (尝试 {attempt + 1}/{settings.llm_max_retries}): {e}")
                if attempt == settings.llm_max_retries - 1:
                    raise
                time.sleep(1)  # 等待1秒后重试

    except Exception as e:
        # 如果API调用失败，抛出异常
        print(f"LLM API调用失败: {e}")
        raise Exception(f"LLM API调用失败: {e}")


def generate_reply(messages: List[Dict[str, str]], role_id: Optional[int] = None, db: Session = None) -> str:
    """
    生成AI回复的主函数
    
    Args:
        messages: 聊天历史记录
        role_id: 角色ID
        db: 数据库会话
    
    Returns:
        str: AI回复内容
    """
    # 获取LLM配置
    api_key, api_url, model, use_rag = get_llm_config()
    
    if use_rag:
        # 使用RAG增强的回复生成
        return generate_reply_with_rag(messages, role_id, db)
    else:
        # 使用真实LLM API（不包含RAG）
        return generate_reply_real_llm(messages, role_id, db)
