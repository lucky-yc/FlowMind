from fastapi import Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size


def get_pagination() -> PaginationParams:
    return PaginationParams()
