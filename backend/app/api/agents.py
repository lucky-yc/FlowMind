from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agent import Agent
from app.models.log import SystemLog
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentListResponse

router = APIRouter(prefix="/agents", tags=["智能体"])


@router.get("", response_model=AgentListResponse)
def list_agents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    agent_type: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Agent).filter(Agent.owner_id == current_user.id)
    if agent_type:
        q = q.filter(Agent.agent_type == agent_type)
    if search:
        q = q.filter(Agent.name.contains(search))
    total = q.count()
    items = q.order_by(Agent.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return AgentListResponse(total=total, items=[AgentResponse.model_validate(a) for a in items])


@router.post("", response_model=AgentResponse)
def create_agent(data: AgentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    agent = Agent(**data.model_dump(), owner_id=current_user.id)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    log = SystemLog(user_id=current_user.id, action="create", resource_type="agent", resource_id=agent.id)
    db.add(log)
    db.commit()
    return AgentResponse.model_validate(agent)


@router.get("/{agent_id}", response_model=AgentResponse)
def get_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == current_user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="智能体不存在")
    return AgentResponse.model_validate(a)


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(agent_id: int, data: AgentUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == current_user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="智能体不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    db.commit()
    db.refresh(a)
    return AgentResponse.model_validate(a)


@router.delete("/{agent_id}")
def delete_agent(agent_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == current_user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="智能体不存在")
    db.delete(a)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{agent_id}/chat")
def agent_chat(agent_id: int, message: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == current_user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="智能体不存在")
    user_msg = message.get("message", "")
    return {
        "response": f"[{a.name}] 收到消息: {user_msg}。这是一个模拟回复，实际部署时将调用 {a.model_name} 模型。",
        "agent_id": a.id,
        "model": a.model_name,
    }
