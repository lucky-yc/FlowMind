from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class LLMModel(Base):
    """模型提供商配置表，存储可供智能体和工作流选择的 LLM 模型"""
    __tablename__ = "llm_models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)  # 显示名称，如 "GPT-4o"
    provider = Column(String(100), nullable=False, default="custom")  # openai / anthropic / custom / ollama ...
    model_id = Column(String(200), nullable=False)  # API 实际标识，如 "gpt-4o"
    base_url = Column(String(500), default="")  # API 端点
    api_key = Column(Text, default="")  # API Key（加密存储推荐，此处简化为明文）
    description = Column(Text, default="")  # 模型说明
    max_tokens = Column(Integer, default=4096)  # 默认最大 token
    supports_streaming = Column(Boolean, default=True)  # 是否支持流式
    supports_vision = Column(Boolean, default=False)  # 是否支持多模态
    config = Column(JSON, default=dict)  # 额外配置（headers、参数范围等）
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="llm_models")
