from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user

# HR_PAYROLL_USER can run the payrun wizard end to end; HR_PAYROLL_MANAGER/
# ADMIN additionally control which salary structures are selectable.
PAYROLL_ROLES = {"HR_PAYROLL_USER", "HR_PAYROLL_MANAGER"}
STRUCTURE_WRITER_ROLES = {"HR_PAYROLL_MANAGER"}


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


def require_payroll_user(current_user: dict = Depends(get_current_user)) -> dict:
    user_roles = set(current_user.get("roles", []))
    if not user_roles & (PAYROLL_ROLES | {"ADMIN"}):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: requires HR_PAYROLL_USER, HR_PAYROLL_MANAGER, or ADMIN role",
        )
    return current_user


def require_structure_writer(current_user: dict = Depends(get_current_user)) -> dict:
    user_roles = set(current_user.get("roles", []))
    if not user_roles & (STRUCTURE_WRITER_ROLES | {"ADMIN"}):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: requires HR_PAYROLL_MANAGER or ADMIN role",
        )
    return current_user


def extract_user_id(current_user: dict) -> Optional[UUID]:
    raw_id = current_user.get("user_id") or current_user.get("id") or current_user.get("sub")
    if not raw_id:
        return None
    try:
        return UUID(str(raw_id))
    except (ValueError, AttributeError):
        return None
