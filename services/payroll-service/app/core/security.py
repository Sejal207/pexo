from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

security = HTTPBearer()

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    return decode_token(credentials.credentials)


def mint_service_token(roles: list[str]) -> str:
    """
    Celery tasks (PDF generation, email) run with no caller in the request
    sense — they still need to call hr-service/attendance-timeoff-service for
    contract/employee/work-entry data. All services trust the same
    SECRET_KEY, so a short-lived, narrowly-scoped token signed here is valid
    everywhere else without a separate service-credential system.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "payroll-service",
        "user_id": None,
        "roles": roles,
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
