"""模型调用日志 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.model_invocation_log import ModelInvocationLog
from app.schemas.model_invocation_log import (
    ModelInvocationLogCreate,
    ModelInvocationLogUpdate,
    ModelInvocationLogResponse,
    ModelInvocationLogListResponse,
    ModelInvocationStats,
)

router = APIRouter()


@router.get("/", response_model=ModelInvocationLogListResponse)
async def list_invocation_logs(
    agent_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    execution_id: Optional[int] = None,
    model_id: Optional[str] = None,
    source_type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型调用日志列表"""
    query = db.query(ModelInvocationLog).filter(
        ModelInvocationLog.user_id == current_user.id
    )
    
    # 应用过滤条件
    if agent_id is not None:
        query = query.filter(ModelInvocationLog.agent_id == agent_id)
    if workflow_id is not None:
        query = query.filter(ModelInvocationLog.workflow_id == workflow_id)
    if execution_id is not None:
        query = query.filter(ModelInvocationLog.execution_id == execution_id)
    if model_id:
        query = query.filter(ModelInvocationLog.model_id.ilike(f"%{model_id}%"))
    if source_type:
        query = query.filter(ModelInvocationLog.source_type == source_type)
    if status:
        query = query.filter(ModelInvocationLog.status == status)
    if start_date:
        query = query.filter(ModelInvocationLog.created_at >= start_date)
    if end_date:
        query = query.filter(ModelInvocationLog.created_at <= end_date)
    
    # 计算总数
    total = query.count()
    
    # 分页查询
    items = (
        query.order_by(ModelInvocationLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    
    return ModelInvocationLogListResponse(total=total, items=items)


@router.get("/stats", response_model=ModelInvocationStats)
async def get_invocation_stats(
    agent_id: Optional[int] = None,
    workflow_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取模型调用统计"""
    query = db.query(ModelInvocationLog).filter(
        ModelInvocationLog.user_id == current_user.id
    )
    
    if agent_id is not None:
        query = query.filter(ModelInvocationLog.agent_id == agent_id)
    if workflow_id is not None:
        query = query.filter(ModelInvocationLog.workflow_id == workflow_id)
    if start_date:
        query = query.filter(ModelInvocationLog.created_at >= start_date)
    if end_date:
        query = query.filter(ModelInvocationLog.created_at <= end_date)
    
    # 总体统计
    total_invocations = query.count()
    successful_invocations = query.filter(ModelInvocationLog.status == "success").count()
    failed_invocations = query.filter(ModelInvocationLog.status == "error").count()
    
    # Token 统计
    token_stats = query.with_entities(
        func.coalesce(func.sum(ModelInvocationLog.total_tokens), 0).label("total_tokens"),
        func.coalesce(func.sum(ModelInvocationLog.prompt_tokens), 0).label("prompt_tokens"),
        func.coalesce(func.sum(ModelInvocationLog.completion_tokens), 0).label("completion_tokens"),
        func.avg(ModelInvocationLog.latency_ms).label("avg_latency_ms"),
    ).first()
    
    # 按模型分组统计
    by_model = {}
    model_stats = (
        query.with_entities(
            ModelInvocationLog.model_id,
            func.count(ModelInvocationLog.id).label("count"),
            func.coalesce(func.sum(ModelInvocationLog.total_tokens), 0).label("tokens"),
        )
        .group_by(ModelInvocationLog.model_id)
        .all()
    )
    for model_id, count, tokens in model_stats:
        by_model[model_id] = {"count": count, "tokens": tokens}
    
    # 按来源分组统计
    by_source = {}
    source_stats = (
        query.with_entities(
            ModelInvocationLog.source_type,
            func.count(ModelInvocationLog.id).label("count"),
        )
        .group_by(ModelInvocationLog.source_type)
        .all()
    )
    for source_type, count in source_stats:
        by_source[source_type] = {"count": count}
    
    # 按状态分组统计
    by_status = {}
    status_stats = (
        query.with_entities(
            ModelInvocationLog.status,
            func.count(ModelInvocationLog.id).label("count"),
        )
        .group_by(ModelInvocationLog.status)
        .all()
    )
    for status, count in status_stats:
        by_status[status] = {"count": count}
    
    return ModelInvocationStats(
        total_invocations=total_invocations,
        successful_invocations=successful_invocations,
        failed_invocations=failed_invocations,
        total_tokens=token_stats.total_tokens,
        prompt_tokens=token_stats.prompt_tokens,
        completion_tokens=token_stats.completion_tokens,
        avg_latency_ms=token_stats.avg_latency_ms,
        by_model=by_model,
        by_source=by_source,
        by_status=by_status,
    )


@router.get("/{log_id}", response_model=ModelInvocationLogResponse)
async def get_invocation_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单条模型调用日志详情"""
    log = (
        db.query(ModelInvocationLog)
        .filter(
            ModelInvocationLog.id == log_id,
            ModelInvocationLog.user_id == current_user.id,
        )
        .first()
    )
    
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    return log


@router.post("/", response_model=ModelInvocationLogResponse)
async def create_invocation_log(
    data: ModelInvocationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建模型调用日志（通常由系统内部调用）"""
    log = ModelInvocationLog(
        user_id=current_user.id,
        status="pending",
        **data.model_dump(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.patch("/{log_id}", response_model=ModelInvocationLogResponse)
async def update_invocation_log(
    log_id: int,
    data: ModelInvocationLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新模型调用日志（记录响应结果）"""
    log = (
        db.query(ModelInvocationLog)
        .filter(
            ModelInvocationLog.id == log_id,
            ModelInvocationLog.user_id == current_user.id,
        )
        .first()
    )
    
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(log, key, value)
    
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}")
async def delete_invocation_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除模型调用日志"""
    log = (
        db.query(ModelInvocationLog)
        .filter(
            ModelInvocationLog.id == log_id,
            ModelInvocationLog.user_id == current_user.id,
        )
        .first()
    )
    
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}
