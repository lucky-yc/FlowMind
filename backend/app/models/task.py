from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    schedule_type = Column(String(20), default="manual")  # manual, cron, interval, once
    schedule_config = Column(JSON, default=dict)
    status = Column(String(20), default="pending")  # pending, running, completed, failed, cancelled
    priority = Column(Integer, default=5)  # 1-10
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    creator = relationship("User", back_populates="tasks")
    executions = relationship("Execution", back_populates="task", cascade="all, delete-orphan")


class Execution(Base):
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    status = Column(String(20), default="running")  # running, completed, failed
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    node_results = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, server_default=func.now())
    finished_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    task = relationship("Task", back_populates="executions")
    workflow = relationship("Workflow", back_populates="executions")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan")


class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=False)
    node_id = Column(String(100), nullable=True)
    level = Column(String(20), default="info")  # info, warning, error, debug
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())

    execution = relationship("Execution", back_populates="logs")
