from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_permission
from app.models import AuditLog, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users(user: User = Depends(require_permission("users:read")), db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(User).where(User.org_id == user.org_id).order_by(User.id))
    return [{"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role, "is_active": u.is_active} for u in rows]


@router.get("/audit-logs")
def audit_logs(limit: int = Query(50, ge=1, le=200), user: User = Depends(require_permission("audit:read")),
               db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(AuditLog).where(AuditLog.org_id == user.org_id).order_by(AuditLog.id.desc()).limit(limit))
    return [{"id": r.id, "user_id": r.user_id, "action": r.action, "resource": r.resource,
             "ip_address": r.ip_address, "created_at": r.created_at.isoformat()} for r in rows]
