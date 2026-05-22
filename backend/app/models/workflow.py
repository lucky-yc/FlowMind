from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default=WorkflowStatus.DRAFT)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    nodes = Column(JSON, default=list)
    edges = Column(JSON, default=list)
    variables = Column(JSON, default=dict)
    config = Column(JSON, default=dict)
    version = Column(Integer, default=1)
    is_template = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="workflows")
    executions = relationship("Execution", back_populates="workflow", cascade="all, delete-orphan")
