from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class LLMModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="模型显示名称")
    provider: str = Field(default="custom", max_length=100, description="提供商类型")
    model_id: str = Field(..., min_length=1, max_length=200, description="API 模型标识")
    base_url: str = Field(default="", max_length=500, description="API 端点")
    api_key: str = Field(default="", description="API Key")
    description: str = Field(default="", description="模型说明")
    max_tokens: int = Field(default=4096, ge=1, le=1000000, description="默认最大 token")
    supports_streaming: bool = Field(default=True, description="是否支持流式输出")
    supports_vision: bool = Field(default=False, description="是否支持多模态/视觉")
    config: dict = Field(default_factory=dict, description="额外配置")


class LLMModelUpdate(BaseModel):
    name: Optional[str] = None
    provider: Optional[str] = None
    model_id: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    description: Optional[str] = None
    max_tokens: Optional[int] = None
    supports_streaming: Optional[bool] = None
    supports_vision: Optional[bool] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class LLMModelResponse(BaseModel):
    id: int
    name: str
    provider: str
    model_id: str
    base_url: str
    api_key: str = ""
    description: str
    max_tokens: int
    supports_streaming: bool
    supports_vision: bool
    config: dict
    owner_id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LLMModelBrief(BaseModel):
    """简要信息，用于下拉选择列表"""
    id: int
    name: str
    provider: str
    model_id: str
    is_active: bool
    supports_vision: bool

    model_config = {"from_attributes": True}


class LLMModelListResponse(BaseModel):
    total: int
    items: list[LLMModelResponse]
