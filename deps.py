import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rbac import role_has
from app.core.security import ALGORITHM
from app.db import get_db
from app.models import AuditLog, User

bearer = HTTPBearer(auto_error=False)
_jwks_client: PyJWKClient | None = None


def _unauthorized() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing credentials", headers={"WWW-Authenticate": "Bearer"})


def _jwks() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(get_settings().oidc_jwks_url, cache_keys=True)
    return _jwks_client


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)
) -> User:
    if creds is None:
        raise _unauthorized()
    s = get_settings()
    try:
        if s.auth_mode == "mock":
            claims = jwt.decode(creds.credentials, s.secret_key, algorithms=[ALGORITHM], issuer="aegisflo-mock")
            user = db.get(User, int(claims["sub"]))
        else:
            key = _jwks().get_signing_key_from_jwt(creds.credentials).key
            claims = jwt.decode(
                creds.credentials, key, algorithms=["RS256", "ES256"], audience=s.oidc_audience, issuer=s.oidc_issuer
            )
            email = str(claims.get(s.oidc_email_claim, "")).lower()
            # Deny by default: the identity must already be provisioned and active in AegisFlo.
            user = db.scalar(select(User).where(User.email == email)) if email else None
    except (jwt.PyJWTError, ValueError, KeyError):
        raise _unauthorized()
    if user is None or not user.is_active:
        raise _unauthorized()
    return user


def require_permission(permission: str):
    def checker(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        if not role_has(user.role, permission):
            db.add(AuditLog(org_id=user.org_id, user_id=user.id, action="access.denied", resource=permission,
                            ip_address=request.client.host if request.client else ""))
            db.commit()
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user

    return checker


def audit(db: Session, request: Request, user: User | None, action: str, resource: str = "", detail: str = "") -> None:
    db.add(AuditLog(org_id=user.org_id if user else None, user_id=user.id if user else None, action=action,
                    resource=resource, detail=detail, ip_address=request.client.host if request.client else ""))
    db.commit()
