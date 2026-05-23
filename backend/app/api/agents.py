from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agent import Agent
from app.models.model_provider import LLMModel
from app.models.log import SystemLog
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentListResponse
from app.services.llm import chat_completion

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
async def agent_chat(agent_id: int, message: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    a = db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == current_user.id).first()
    if not a:
        raise HTTPException(status_code=404, detail="智能体不存在")
    
    user_msg = message.get("message", "")
    if not user_msg.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")
    
    # 查找智能体使用的模型配置
    model_config = db.query(LLMModel).filter(
        LLMModel.model_id == a.model_name,
        LLMModel.owner_id == current_user.id,
        LLMModel.is_active == True
    ).first()
    
    # 如果找不到精确匹配，尝试模糊匹配
    if not model_config:
        model_config = db.query(LLMModel).filter(
            LLMModel.name.contains(a.model_name),
            LLMModel.owner_id == current_user.id,
            LLMModel.is_active == True
        ).first()
    
    # 如果仍然找不到，返回提示
    if not model_config:
        return {
            "response": f"⚠️ 未找到模型 \"{a.model_name}\" 的配置。请先在「模型管理」中添加对应的模型配置。",
            "agent_id": a.id,
            "model": a.model_name,
            "error": "model_not_found"
        }
    
    # 构建消息列表
    messages = []
    
    # 添加系统提示词
    if a.system_prompt:
        messages.append({"role": "system", "content": a.system_prompt})
    
    # 添加用户消息
    messages.append({"role": "user", "content": user_msg})
    
    # 计算 temperature（Agent 存储为 0-100，需要转换为 0-2）
    temperature = (a.temperature or 70) / 50.0  # 70 -> 1.4，范围 0-2
    
    # 使用智能体配置的 max_tokens 或模型默认值
    max_tokens = a.max_tokens or model_config.max_tokens or 4096
    
    try:
        # 调用 LLM 服务（附带日志记录）
        response_text = await chat_completion(
            model=model_config,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            db=db,
            user_id=current_user.id,
            agent_id=a.id,
            source_type="agent",
            source_name=a.name,
        )
        
        return {
            "response": response_text,
            "agent_id": a.id,
            "model": a.model_name,
        }
    except ValueError as e:
        return {
            "response": f"❌ 模型调用失败: {str(e)}",
            "agent_id": a.id,
            "model": a.model_name,
            "error": "model_call_failed"
        }
    except Exception as e:
        return {
            "response": f"❌ 发生未知错误: {str(e)}",
            "agent_id": a.id,
            "model": a.model_name,
            "error": "unknown_error"
        }
