from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ModelInvocationLog(Base):
    """模型调用日志 - 记录工作流和智能体的模型调用详情"""
    __tablename__ = "model_invocation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联信息
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    execution_id = Column(Integer, ForeignKey("executions.id"), nullable=True)
    node_id = Column(String(100), nullable=True)  # 工作流节点ID
    
    # 模型信息
    model_provider = Column(String(50), nullable=False)  # openai, anthropic, custom
    model_id = Column(String(100), nullable=False)  # gpt-4, claude-3, etc.
    model_name = Column(String(100), nullable=True)  # 用户定义的模型名称
    
    # 调用参数
    temperature = Column(Float, nullable=True)
    max_tokens = Column(Integer, nullable=True)
    request_params = Column(JSON, default=dict)  # 其他请求参数
    
    # 请求内容
    system_prompt = Column(Text, nullable=True)
    input_messages = Column(JSON, nullable=True)  # 输入消息列表
    
    # 响应内容
    output_content = Column(Text, nullable=True)
    response_metadata = Column(JSON, default=dict)  # 响应元数据
    
    # Token 使用统计
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    # 性能统计
    latency_ms = Column(Integer, nullable=True)  # 请求耗时(毫秒)
    
    # 状态信息
    status = Column(String(20), default="pending")  # pending, success, error, timeout
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    
    # 调用来源
    source_type = Column(String(20), nullable=False)  # agent, workflow, api
    source_name = Column(String(200), nullable=True)  # 智能体/工作流名称
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    user = relationship("User", back_populates="model_invocation_logs")
    agent = relationship("Agent", back_populates="model_invocation_logs")
    workflow = relationship("Workflow", back_populates="model_invocation_logs")
    execution = relationship("Execution", back_populates="model_invocation_logs")
