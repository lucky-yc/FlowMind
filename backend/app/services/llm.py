"""LLM 服务 - 调用真实模型进行对话"""
import httpx
from typing import Optional
from app.models.model_provider import LLMModel


async def chat_completion(
    model: LLMModel,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """调用 LLM 模型进行对话
    
    支持 OpenAI 兼容的 API 格式（包括 OpenAI、Azure、自定义端点、Ollama 等）
    """
    if not model.base_url or not model.api_key:
        raise ValueError(f"模型 {model.name} 未配置 base_url 或 api_key")
    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {model.api_key}",
    }
    
    # 合并额外配置中的 headers
    if model.config and "headers" in model.config:
        headers.update(model.config["headers"])
    
    # 构建请求体
    payload = {
        "model": model.model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,  # 暂不支持流式
    }
    
    # 合并额外配置中的参数
    if model.config and "params" in model.config:
        payload.update(model.config["params"])
    
    # 确保 URL 以正确格式结尾
    base_url = model.base_url.rstrip("/")
    
    # 根据 provider 选择不同的端点
    if model.provider == "anthropic":
        # Anthropic 使用不同的 API 格式
        return await _call_anthropic(base_url, model.api_key, messages, model.model_id, temperature, max_tokens)
    else:
        # OpenAI 兼容格式（适用于 OpenAI、自定义端点、Ollama 等）
        url = f"{base_url}/v1/chat/completions"
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # 提取回复内容
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise ValueError(f"API 返回格式异常: {data}")
                    
            except httpx.HTTPStatusError as e:
                raise ValueError(f"API 调用失败 (HTTP {e.response.status_code}): {e.response.text}")
            except httpx.RequestError as e:
                raise ValueError(f"网络请求失败: {str(e)}")


async def _call_anthropic(
    base_url: str,
    api_key: str,
    messages: list[dict],
    model_id: str,
    temperature: float,
    max_tokens: int,
) -> str:
    """调用 Anthropic Claude API"""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    
    # 分离系统消息
    system_msg = ""
    chat_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system_msg = msg["content"]
        else:
            chat_messages.append(msg)
    
    payload = {
        "model": model_id,
        "messages": chat_messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    if system_msg:
        payload["system"] = system_msg
    
    url = f"{base_url}/v1/messages"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if "content" in data and len(data["content"]) > 0:
                return data["content"][0]["text"]
            else:
                raise ValueError(f"Anthropic API 返回格式异常: {data}")
                
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Anthropic API 调用失败 (HTTP {e.response.status_code}): {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"网络请求失败: {str(e)}")
