"""LLM 服务 - 调用真实模型进行对话"""
import time
import httpx
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from app.models.model_provider import LLMModel
from app.services.invocation_log import (
    log_invocation,
    update_log_success,
    update_log_error,
    extract_token_usage,
)


async def chat_completion(
    model: LLMModel,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 4096,
    # 日志相关参数
    db: Optional[Session] = None,
    user_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    execution_id: Optional[int] = None,
    node_id: Optional[str] = None,
    source_type: str = "api",
    source_name: Optional[str] = None,
) -> str:
    """调用 LLM 模型进行对话
    
    支持 OpenAI 兼容的 API 格式（包括 OpenAI、Azure、自定义端点、Ollama 等）
    
    Args:
        model: LLM 模型配置
        messages: 消息列表
        temperature: 温度参数
        max_tokens: 最大 token 数
        db: 数据库会话（用于日志记录）
        user_id: 用户 ID
        agent_id: 智能体 ID
        workflow_id: 工作流 ID
        execution_id: 执行 ID
        node_id: 节点 ID
        source_type: 调用来源类型 (agent, workflow, api)
        source_name: 调用来源名称
    """
    if not model.base_url or not model.api_key:
        raise ValueError(f"模型 {model.name} 未配置 base_url 或 api_key")
    
    # 创建日志记录
    log_id = None
    if db:
        log = await log_invocation(
            db=db,
            user_id=user_id,
            agent_id=agent_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            node_id=node_id,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            source_type=source_type,
            source_name=source_name,
        )
        log_id = log.id
    
    # 记录开始时间
    start_time = time.time()
    
    try:
        # 根据 provider 选择调用方式
        if model.provider == "anthropic":
            result, response_data = await _call_anthropic_with_response(
                model.base_url, model.api_key, messages, model.model_id, temperature, max_tokens
            )
        else:
            result, response_data = await _call_openai_compatible_with_response(
                model, messages, temperature, max_tokens
            )
        
        # 计算耗时
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 更新日志 - 成功
        if db and log_id:
            token_usage = extract_token_usage(response_data)
            await update_log_success(
                db=db,
                log_id=log_id,
                output_content=result,
                response_metadata=response_data,
                latency_ms=latency_ms,
                **token_usage,
            )
        
        return result
        
    except Exception as e:
        # 计算耗时
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 更新日志 - 失败
        if db and log_id:
            error_code = None
            if isinstance(e, httpx.HTTPStatusError):
                error_code = str(e.response.status_code)
            elif isinstance(e, ValueError):
                error_code = "VALUE_ERROR"
            
            await update_log_error(
                db=db,
                log_id=log_id,
                error_message=str(e),
                error_code=error_code,
                latency_ms=latency_ms,
            )
        
        # 重新抛出异常
        raise


async def _call_openai_compatible_with_response(
    model: LLMModel,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: int,
) -> tuple:
    """调用 OpenAI 兼容 API，返回结果和原始响应"""
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
        "stream": False,
    }
    
    # 合并额外配置中的参数
    if model.config and "params" in model.config:
        payload.update(model.config["params"])
    
    # 确保 URL 以正确格式结尾
    base_url = model.base_url.rstrip("/")
    url = f"{base_url}/v1/chat/completions"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # 提取回复内容
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return content, data
            else:
                raise ValueError(f"API 返回格式异常: {data}")
                
        except httpx.HTTPStatusError as e:
            raise ValueError(f"API 调用失败 (HTTP {e.response.status_code}): {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"网络请求失败: {str(e)}")


async def _call_anthropic_with_response(
    base_url: str,
    api_key: str,
    messages: List[Dict[str, str]],
    model_id: str,
    temperature: float,
    max_tokens: int,
) -> tuple:
    """调用 Anthropic Claude API，返回结果和原始响应"""
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
                content = data["content"][0]["text"]
                # 转换 Anthropic 响应格式以统一 token 统计
                usage = data.get("usage", {})
                normalized_data = {
                    "usage": {
                        "prompt_tokens": usage.get("input_tokens"),
                        "completion_tokens": usage.get("output_tokens"),
                        "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                    },
                    "raw_response": data,
                }
                return content, normalized_data
            else:
                raise ValueError(f"Anthropic API 返回格式异常: {data}")
                
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Anthropic API 调用失败 (HTTP {e.response.status_code}): {e.response.text}")
        except httpx.RequestError as e:
            raise ValueError(f"网络请求失败: {str(e)}")


# 保持向后兼容的旧接口
async def chat_completion_legacy(
    model: LLMModel,
    messages: list[dict],
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """旧版接口 - 不记录日志"""
    return await chat_completion(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
