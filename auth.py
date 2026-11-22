from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rbac import PERMISSIONS
from app.core.security import create_access_token
from app.db import get_db
from app.deps import audit, get_current_user
from app.models import Organization, User

router = APIRouter(prefix="/auth", tags=["auth"])


class MockLogin(BaseModel):
    email: str


def user_out(u: User, org_name: str) -> dict:
    return {"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role, "organization": org_name,
            "permissions": sorted(PERMISSIONS.get(u.role, set()))}


def _require_mock() -> None:
    if get_settings().auth_mode != "mock":
        raise HTTPException(404, "Not found")


@router.get("/config")
def auth_config() -> dict:
    return {"mode": get_settings().auth_mode}


@router.get("/demo-users")
def demo_users(db: Session = Depends(get_db)) -> list[dict]:
    _require_mock()
    return [{"email": u.email, "full_name": u.full_name, "role": u.role}
            for u in db.scalars(select(User).where(User.is_active).order_by(User.id))]


@router.post("/mock-login")
def mock_login(body: MockLogin, request: Request, db: Session = Depends(get_db)) -> dict:
    _require_mock()
    user = db.scalar(select(User).where(User.email == body.email.strip().lower()))
    if user is None or not user.is_active:
        audit(db, request, None, "auth.login_failed", body.email[:200])
        raise HTTPException(401, "Unknown or inactive account")
    audit(db, request, user, "auth.login", user.email)
    org = db.get(Organization, user.org_id)
    return {"access_token": create_access_token(user.id), "token_type": "bearer", "user": user_out(user, org.name)}


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    return user_out(user, db.get(Organization, user.org_id).name)
