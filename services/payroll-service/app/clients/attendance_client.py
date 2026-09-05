"""
Thin HTTP client to attendance-timeoff-service: pulls approved-leave
deductions for a payroll period (Pipeline 3 -> Pipeline 5 integration point),
grouped by `payroll_work_entry_code`. Values are injected into the rule
engine's evaluation context so FORMULA rules can reference them by code.
"""
from datetime import date
from uuid import UUID

import httpx
from fastapi import HTTPException

from app.core.config import settings


class AttendanceClient:
    def __init__(self, bearer_token: str) -> None:
        self._headers = {"Authorization": f"Bearer {bearer_token}"}

    async def get_work_entries(
        self, *, employee_id: UUID, period_start: date, period_end: date
    ) -> list[dict]:
        params = {
            "employee_id": str(employee_id),
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
        }
        async with httpx.AsyncClient(
            base_url=settings.ATTENDANCE_SERVICE_URL, timeout=10.0
        ) as client:
            try:
                resp = await client.get(
                    "/api/v1/time-off/work-entries", params=params, headers=self._headers
                )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=502, detail=f"attendance-timeoff-service unreachable: {exc}"
                ) from exc

        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code if resp.status_code in (401, 403) else 502,
                detail=f"attendance-timeoff-service work-entries lookup failed: {resp.text}",
            )
        return resp.json()
