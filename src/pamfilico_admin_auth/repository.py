"""Generic user repository: counts + paginates any SQLAlchemy user-like model."""

import math
from typing import Any, Dict, List, Tuple, Type

from sqlalchemy import func
from sqlalchemy.orm import Session


class AdminUserRepository:
    """
    Generic repo that operates on any SQLAlchemy model with ``email`` and
    ``created_at`` columns. The host app's User model is injected at construction
    time rather than imported from a fixed module path.
    """

    def __init__(self, session: Session, user_model: Type[Any]):
        self.session = session
        self.user_model = user_model

    def count_with_email_filter(self, email_contains: str) -> int:
        q = self.session.query(self.user_model).filter(self.user_model.email.isnot(None))
        ec = (email_contains or "").strip()
        if ec:
            q = q.filter(func.lower(self.user_model.email).contains(ec.lower()))
        return q.count()

    def list_paginated(
        self, page: int, page_size: int, email_contains: str
    ) -> List[Any]:
        q = self.session.query(self.user_model).filter(self.user_model.email.isnot(None))
        ec = (email_contains or "").strip()
        if ec:
            q = q.filter(func.lower(self.user_model.email).contains(ec.lower()))
        q = q.order_by(self.user_model.created_at.desc())
        offset = (page - 1) * page_size
        return q.offset(offset).limit(page_size).all()

    def paginate(
        self, current_page: int, page_size: int, email_contains: str
    ) -> Tuple[List[Any], Dict[str, Any]]:
        """Return (rows, pagination_dict) in one call."""
        total = self.count_with_email_filter(email_contains)
        rows = self.list_paginated(current_page, page_size, email_contains)
        total_pages = max(1, math.ceil(total / page_size)) if page_size else 1
        pagination: Dict[str, Any] = {
            "currentPage": current_page,
            "pageSize": page_size,
            "totalCount": total,
            "totalPages": total_pages,
            "nextPage": current_page + 1 if current_page < total_pages else None,
            "previousPage": current_page - 1 if current_page > 1 else None,
        }
        return rows, pagination
