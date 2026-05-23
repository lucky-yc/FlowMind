"""模型调用日志服务 - 记录 LLM 调用详情"""
import time
import json
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.model_invocation_log import ModelInvocationLog
from app.models.model_provider import LLMModel


async def log_invocation(
    db: Session,
    *,
    user_id: Optional[int] = None,
    agent_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    execution_id: Optional[int] = None,
    node_id: Optional[str] = None,
    model: LLMModel,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 4096,
    source_type: str = "api",
    source_name: Optional[str] = None,
) -> ModelInvocationLog:
    """创建模型调用日志记录"""
    # 提取系统提示词
    system_prompt = None
    input_messages = []
    for msg in messages:
        if msg.get("role") == "system":
            system_prompt = msg.get("content")
        else:
            input_messages.append(msg)
    
    log = ModelInvocationLog(
        user_id=user_id,
        agent_id=agent_id,
        workflow_id=workflow_id,
        execution_id=execution_id,
        node_id=node_id,
        model_provider=model.provider or "openai",
        model_id=model.model_id,
        model_name=model.name,
        temperature=temperature,
        max_tokens=max_tokens,
        request_params={},
        system_prompt=system_prompt,
        input_messages=input_messages,
        source_type=source_type,
        source_name=source_name,
        status="pending",
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log


async def update_log_success(
    db: Session,
    log_id: int,
    *,
    output_content: str,
    response_metadata: Optional[Dict[str, Any]] = None,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    latency_ms: int,
) -> None:
    """更新日志记录 - 成功"""
    log = db.query(ModelInvocationLog).filter(ModelInvocationLog.id == log_id).first()
    if not log:
        return
    
    log.output_content = output_content
    log.response_metadata = response_metadata or {}
    log.prompt_tokens = prompt_tokens
    log.completion_tokens = completion_tokens
    log.total_tokens = total_tokens
    log.latency_ms = latency_ms
    log.status = "success"
    
    db.commit()


async def update_log_error(
    db: Session,
    log_id: int,
    *,
    error_message: str,
    error_code: Optional[str] = None,
    latency_ms: int,
) -> None:
    """更新日志记录 - 失败"""
    log = db.query(ModelInvocationLog).filter(ModelInvocationLog.id == log_id).first()
    if not log:
        return
    
    log.error_message = error_message
    log.error_code = error_code
    log.latency_ms = latency_ms
    log.status = "error"
    
    db.commit()


def extract_token_usage(response_data: dict) -> dict:
    """从 API 响应中提取 token 使用信息"""
    usage = response_data.get("usage", {})
    return {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }
