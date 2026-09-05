from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user

def require_role(allowed_roles: list[str]):
    def role_checker(user: dict = Depends(get_current_user)):
        roles = user.get("roles", [])
        if not any(role in allowed_roles for role in roles) and "ADMIN" not in roles:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user
    return role_checker
