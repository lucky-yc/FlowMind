from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    agent_type: str = "chatbot"
    model_name: str = "gpt-4"
    system_prompt: str = ""
    temperature: int = Field(default=70, ge=0, le=100)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    tools: list[dict] = Field(default_factory=list)
    knowledge_bases: list[str] = Field(default_factory=list)
    config: dict = Field(default_factory=dict)


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None
    model_name: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[int] = None
    max_tokens: Optional[int] = None
    tools: Optional[list[dict]] = None
    knowledge_bases: Optional[list[str]] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    id: int
    name: str
    description: str
    agent_type: str
    model_name: str
    system_prompt: str
    temperature: int
    max_tokens: int
    tools: list[Any]
    knowledge_bases: list[Any]
    config: dict
    owner_id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    total: int
    items: list[AgentResponse]
