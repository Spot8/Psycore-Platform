from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    s = get_settings()
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "iat": now, "exp": now + timedelta(minutes=s.access_token_minutes), "iss": "aegisflo-mock"}
    return jwt.encode(payload, s.secret_key, algorithm=ALGORITHM)
