from typing import Optional, Any
from uuid import UUID
from fastapi import Depends, HTTPException, status
from app.core.security import get_current_user

WRITER_ROLES = {"HR_MANAGER", "HR_PAYROLL_MANAGER", "ADMIN"}
PAYROLL_READ_ROLES = {"HR_PAYROLL_USER", "HR_PAYROLL_MANAGER", "ADMIN"}


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


def scope_to_own_employee(
    employee_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> dict:
    """EMPLOYEE role can only access their own record."""
    roles = current_user.get("roles", [])
    if roles == ["EMPLOYEE"] or (len(roles) == 1 and "EMPLOYEE" in roles):
        user_emp_id = current_user.get("employee_id")
        if not user_emp_id or str(user_emp_id) != str(employee_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to other employees' records is not allowed",
            )
    return current_user
