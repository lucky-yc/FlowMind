from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.model_provider import LLMModel
from app.models.log import SystemLog
from app.schemas.model_provider import (
    LLMModelCreate, LLMModelUpdate, LLMModelResponse,
    LLMModelBrief, LLMModelListResponse,
)

router = APIRouter(prefix="/models", tags=["模型管理"])


@router.get("", response_model=LLMModelListResponse)
def list_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    provider: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = Query(False, description="仅返回启用的模型"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(LLMModel).filter(LLMModel.owner_id == current_user.id)
    if provider:
        q = q.filter(LLMModel.provider == provider)
    if search:
        q = q.filter(LLMModel.name.contains(search))
    if active_only:
        q = q.filter(LLMModel.is_active == True)
    total = q.count()
    items = q.order_by(LLMModel.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return LLMModelListResponse(
        total=total,
        items=[LLMModelResponse.model_validate(m) for m in items],
    )


@router.get("/brief", response_model=list[LLMModelBrief])
def list_models_brief(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """返回启用模型的简要列表，供下拉选择使用"""
    items = (
        db.query(LLMModel)
        .filter(LLMModel.owner_id == current_user.id, LLMModel.is_active == True)
        .order_by(LLMModel.name)
        .all()
    )
    return [LLMModelBrief.model_validate(m) for m in items]


@router.post("", response_model=LLMModelResponse)
def create_model(data: LLMModelCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    model = LLMModel(**data.model_dump(), owner_id=current_user.id)
    db.add(model)
    db.commit()
    db.refresh(model)
    log = SystemLog(user_id=current_user.id, action="create", resource_type="llm_model", resource_id=model.id)
    db.add(log)
    db.commit()
    return LLMModelResponse.model_validate(model)


@router.get("/{model_id}", response_model=LLMModelResponse)
def get_model(model_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = db.query(LLMModel).filter(LLMModel.id == model_id, LLMModel.owner_id == current_user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="模型不存在")
    return LLMModelResponse.model_validate(m)


@router.put("/{model_id}", response_model=LLMModelResponse)
def update_model(model_id: int, data: LLMModelUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = db.query(LLMModel).filter(LLMModel.id == model_id, LLMModel.owner_id == current_user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="模型不存在")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(m, field, value)
    db.commit()
    db.refresh(m)
    return LLMModelResponse.model_validate(m)


@router.delete("/{model_id}")
def delete_model(model_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = db.query(LLMModel).filter(LLMModel.id == model_id, LLMModel.owner_id == current_user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="模型不存在")
    db.delete(m)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{model_id}/toggle")
def toggle_model(model_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """切换模型启用/停用状态"""
    m = db.query(LLMModel).filter(LLMModel.id == model_id, LLMModel.owner_id == current_user.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="模型不存在")
    m.is_active = not m.is_active
    db.commit()
    db.refresh(m)
    return {"id": m.id, "is_active": m.is_active}
