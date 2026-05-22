from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), default="")
    avatar_url = Column(String(500), default="")
    role = Column(String(20), default="user")  # admin, editor, user
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    workflows = relationship("Workflow", back_populates="owner", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="creator", cascade="all, delete-orphan")
