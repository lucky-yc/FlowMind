from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.workflow import Workflow
from app.models.task import Execution, ExecutionLog
from app.models.log import SystemLog
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowListResponse
from app.schemas.task import ExecutionResponse
import json

router = APIRouter(prefix="/workflows", tags=["工作流"])


@router.get("", response_model=WorkflowListResponse)
def list_workflows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Workflow).filter(Workflow.owner_id == current_user.id)
    if status:
        q = q.filter(Workflow.status == status)
    if search:
        q = q.filter(Workflow.name.contains(search))
    total = q.count()
    items = q.order_by(Workflow.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return WorkflowListResponse(total=total, items=[WorkflowResponse.model_validate(w) for w in items])


@router.post("", response_model=WorkflowResponse)
def create_workflow(data: WorkflowCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workflow = Workflow(**data.model_dump(), owner_id=current_user.id)
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    log = SystemLog(user_id=current_user.id, action="create", resource_type="workflow", resource_id=workflow.id)
    db.add(log)
    db.commit()
    return WorkflowResponse.model_validate(workflow)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    w = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="工作流不存在")
    return WorkflowResponse.model_validate(w)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: int, data: WorkflowUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    w = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="工作流不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(w, field, value)
    w.version += 1
    db.commit()
    db.refresh(w)
    return WorkflowResponse.model_validate(w)


@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    w = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="工作流不存在")
    db.delete(w)
    db.commit()
    log = SystemLog(user_id=current_user.id, action="delete", resource_type="workflow", resource_id=workflow_id)
    db.add(log)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{workflow_id}/execute", response_model=ExecutionResponse)
def execute_workflow(workflow_id: int, input_data: dict = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    w = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="工作流不存在")
    execution = Execution(
        workflow_id=workflow_id,
        status="running",
        input_data=input_data or {},
        node_results={},
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    # Simulate execution with node results
    results = {}
    for node in (w.nodes or []):
        node_id = node.get("id", "unknown")
        results[node_id] = {"status": "completed", "output": f"Node {node_id} executed"}
    execution.status = "completed"
    execution.output_data = {"message": "工作流执行完成"}
    execution.node_results = results
    from datetime import datetime
    execution.finished_at = datetime.utcnow()
    log_entry = ExecutionLog(execution_id=execution.id, level="info", message="工作流执行完成")
    db.add(log_entry)
    sys_log = SystemLog(user_id=current_user.id, action="execute", resource_type="workflow", resource_id=workflow_id)
    db.add(sys_log)
    db.commit()
    db.refresh(execution)
    return ExecutionResponse.model_validate(execution)


@router.get("/{workflow_id}/executions", response_model=list[ExecutionResponse])
def get_workflow_executions(workflow_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    w = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id).first()
    if not w:
        raise HTTPException(status_code=404, detail="工作流不存在")
    execs = db.query(Execution).filter(Execution.workflow_id == workflow_id).order_by(Execution.started_at.desc()).limit(50).all()
    return [ExecutionResponse.model_validate(e) for e in execs]
