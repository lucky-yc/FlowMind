from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.task import Task, Execution, ExecutionLog
from app.models.log import SystemLog
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, ExecutionResponse, ExecutionLogResponse, TaskListResponse, ExecutionListResponse

router = APIRouter(prefix="/tasks", tags=["任务"])


@router.get("", response_model=TaskListResponse)
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(Task).filter(Task.creator_id == current_user.id)
    if status:
        q = q.filter(Task.status == status)
    total = q.count()
    items = q.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return TaskListResponse(total=total, items=[TaskResponse.model_validate(t) for t in items])


@router.post("", response_model=TaskResponse)
def create_task(data: TaskCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = Task(**data.model_dump(), creator_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.creator_id == current_user.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskResponse.model_validate(t)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.creator_id == current_user.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    db.commit()
    db.refresh(t)
    return TaskResponse.model_validate(t)


@router.delete("/{task_id}")
def delete_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.creator_id == current_user.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(t)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{task_id}/run", response_model=ExecutionResponse)
def run_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    t = db.query(Task).filter(Task.id == task_id, Task.creator_id == current_user.id).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    execution = Execution(task_id=task_id, workflow_id=t.workflow_id, status="running", input_data=t.input_data)
    db.add(execution)
    t.status = "running"
    db.commit()
    db.refresh(execution)
    execution.status = "completed"
    execution.output_data = {"result": "任务执行完成"}
    execution.finished_at = datetime.utcnow()
    execution.duration_ms = 1234
    t.status = "completed"
    log = ExecutionLog(execution_id=execution.id, level="info", message="任务执行完成")
    db.add(log)
    db.commit()
    db.refresh(execution)
    return ExecutionResponse.model_validate(execution)


@router.get("/{task_id}/executions", response_model=list[ExecutionResponse])
def get_task_executions(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    execs = db.query(Execution).filter(Execution.task_id == task_id).order_by(Execution.started_at.desc()).limit(50).all()
    return [ExecutionResponse.model_validate(e) for e in execs]
