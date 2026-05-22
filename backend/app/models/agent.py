from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    agent_type = Column(String(50), default="chatbot")  # chatbot, assistant, tool, workflow
    model_name = Column(String(100), default="gpt-4")
    system_prompt = Column(Text, default="")
    temperature = Column(Integer, default=70)  # 0-100, stored as int to avoid float issues
    max_tokens = Column(Integer, default=4096)
    tools = Column(JSON, default=list)
    knowledge_bases = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="agents")
