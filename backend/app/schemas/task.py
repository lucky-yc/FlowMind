from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class TaskCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    workflow_id: Optional[int] = None
    agent_id: Optional[int] = None
    schedule_type: str = "manual"
    schedule_config: dict = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)
    input_data: dict = Field(default_factory=dict)


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_config: Optional[dict] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    input_data: Optional[dict] = None


class TaskResponse(BaseModel):
    id: int
    name: str
    description: str
    workflow_id: Optional[int] = None
    agent_id: Optional[int] = None
    creator_id: int
    schedule_type: str
    schedule_config: dict
    status: str
    priority: int
    input_data: dict
    output_data: dict
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExecutionResponse(BaseModel):
    id: int
    task_id: Optional[int] = None
    workflow_id: Optional[int] = None
    status: str
    input_data: dict
    output_data: dict
    node_results: dict
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    model_config = {"from_attributes": True}


class ExecutionLogResponse(BaseModel):
    id: int
    execution_id: int
    node_id: Optional[str] = None
    level: str
    message: str
    data: Optional[dict] = None
    timestamp: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    total: int
    items: list[TaskResponse]


class ExecutionListResponse(BaseModel):
    total: int
    items: list[ExecutionResponse]
