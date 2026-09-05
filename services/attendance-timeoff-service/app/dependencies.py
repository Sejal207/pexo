from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user

WRITER_ROLES = {"HR_MANAGER", "HR_PAYROLL_MANAGER", "ADMIN"}
READ_ALL_ROLES = WRITER_ROLES


def require_writer(current_user: dict = Depends(get_current_user)) -> dict:
    user_roles = set(current_user.get("roles", []))
    if not user_roles & WRITER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: requires HR_MANAGER, HR_PAYROLL_MANAGER, or ADMIN role",
        )
    return current_user


def require_any_role(*roles: str):
    allowed = set(roles) | {"ADMIN"}

    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = set(current_user.get("roles", []))
        if not user_roles & allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: requires one of {list(roles)}",
            )
        return current_user

    return role_checker


def get_self_employee_id(current_user: dict) -> Optional[UUID]:
    raw = current_user.get("employee_id")
    if not raw:
        return None
    try:
        return UUID(str(raw))
    except (ValueError, AttributeError):
        return None


def require_employee_link(current_user: dict = Depends(get_current_user)) -> UUID:
    """
    Check-in/check-out/widget-status always act on the caller's own employee
    record. Per Pipeline 0, every `user` is linked to exactly one `employee`, so
    the token must carry an `employee_id` claim for these endpoints to mean
    anything.
    """
    employee_id = get_self_employee_id(current_user)
    if not employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account is not linked to an employee record",
        )
    return employee_id
