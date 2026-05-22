from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class NodePosition(BaseModel):
    x: float = 0
    y: float = 0


class NodeData(BaseModel):
    label: str = ""
    node_type: str = "llm"
    config: dict = Field(default_factory=dict)
    description: str = ""


class WorkflowNode(BaseModel):
    id: str
    type: str
    position: NodePosition
    data: NodeData
    width: Optional[int] = None
    height: Optional[int] = None


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None
    label: Optional[str] = None
    animated: bool = False
    type: str = "smoothstep"


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    nodes: list[dict] = Field(default_factory=list)
    edges: list[dict] = Field(default_factory=list)
    variables: dict = Field(default_factory=dict)
    config: dict = Field(default_factory=dict)
    is_template: bool = False


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    nodes: Optional[list[dict]] = None
    edges: Optional[list[dict]] = None
    variables: Optional[dict] = None
    config: Optional[dict] = None


class WorkflowResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    owner_id: int
    nodes: list[Any]
    edges: list[Any]
    variables: dict
    config: dict
    version: int
    is_template: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class WorkflowListResponse(BaseModel):
    total: int
    items: list[WorkflowResponse]
