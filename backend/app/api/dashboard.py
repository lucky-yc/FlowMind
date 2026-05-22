from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workflow import Workflow
from app.models.agent import Agent
from app.models.task import Task, Execution

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/stats")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    uid = current_user.id
    workflow_count = db.query(func.count(Workflow.id)).filter(Workflow.owner_id == uid).scalar() or 0
    agent_count = db.query(func.count(Agent.id)).filter(Agent.owner_id == uid).scalar() or 0
    task_count = db.query(func.count(Task.id)).filter(Task.creator_id == uid).scalar() or 0
    execution_count = db.query(func.count(Execution.id)).join(Workflow, Execution.workflow_id == Workflow.id, isouter=True).filter(
        (Execution.task_id.in_(db.query(Task.id).filter(Task.creator_id == uid))) |
        (Workflow.owner_id == uid)
    ).scalar() or 0
    active_workflows = db.query(func.count(Workflow.id)).filter(Workflow.owner_id == uid, Workflow.status == "active").scalar() or 0
    recent_executions = db.query(Execution).join(Workflow, Execution.workflow_id == Workflow.id, isouter=True).filter(
        Workflow.owner_id == uid
    ).order_by(Execution.started_at.desc()).limit(10).all()

    return {
        "workflow_count": workflow_count,
        "agent_count": agent_count,
        "task_count": task_count,
        "execution_count": execution_count,
        "active_workflows": active_workflows,
        "recent_executions": [
            {
                "id": e.id,
                "status": e.status,
                "workflow_id": e.workflow_id,
                "started_at": e.started_at.isoformat() if e.started_at else None,
                "duration_ms": e.duration_ms,
            }
            for e in recent_executions
        ],
    }
