from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime


class ModelInvocationLogCreate(BaseModel):
    """创建模型调用日志的请求"""
    agent_id: Optional[int] = None
    workflow_id: Optional[int] = None
    execution_id: Optional[int] = None
    node_id: Optional[str] = None
    
    model_provider: str
    model_id: str
    model_name: Optional[str] = None
    
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    request_params: dict = Field(default_factory=dict)
    
    system_prompt: Optional[str] = None
    input_messages: Optional[List[dict]] = None
    
    source_type: str = "api"  # agent, workflow, api
    source_name: Optional[str] = None


class ModelInvocationLogUpdate(BaseModel):
    """更新模型调用日志（用于记录响应）"""
    output_content: Optional[str] = None
    response_metadata: Optional[dict] = None
    
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    latency_ms: Optional[int] = None
    
    status: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class ModelInvocationLogResponse(BaseModel):
    """模型调用日志响应"""
    id: int
    
    user_id: Optional[int] = None
    agent_id: Optional[int] = None
    workflow_id: Optional[int] = None
    execution_id: Optional[int] = None
    node_id: Optional[str] = None
    
    model_provider: str
    model_id: str
    model_name: Optional[str] = None
    
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    request_params: dict
    
    system_prompt: Optional[str] = None
    input_messages: Optional[List[dict]] = None
    
    output_content: Optional[str] = None
    response_metadata: dict
    
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    
    latency_ms: Optional[int] = None
    
    status: str
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    source_type: str
    source_name: Optional[str] = None
    
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ModelInvocationLogListResponse(BaseModel):
    """模型调用日志列表响应"""
    total: int
    items: List[ModelInvocationLogResponse]


class ModelInvocationStats(BaseModel):
    """模型调用统计"""
    total_invocations: int
    successful_invocations: int
    failed_invocations: int
    
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    
    avg_latency_ms: Optional[float] = None
    
    by_model: dict = Field(default_factory=dict)  # 按模型分组统计
    by_source: dict = Field(default_factory=dict)  # 按来源分组统计
    by_status: dict = Field(default_factory=dict)  # 按状态分组统计
