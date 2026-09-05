"""
Thin HTTP client to hr-service, used only to resolve which Working Schedule
applies to an employee on a given date (Pipeline 1b -> Pipeline 2 dependency).

Every call forwards the original caller's bearer token rather than minting a
service-to-service credential: hr-service's own role checks (EMPLOYEE can read
their own contract/schedule; HR_MANAGER+ can read anyone's) already cover every
caller this service will ever proxy for, so there is nothing extra to enforce
here. Failures degrade silently to "no schedule found" — a missing or
unreachable hr-service should never block a check-out.
"""
from datetime import date
from typing import Optional
from uuid import UUID

import httpx

from app.core.config import settings


class HRClient:
    def __init__(self, bearer_token: str) -> None:
        self._headers = {"Authorization": f"Bearer {bearer_token}"}

    async def get_working_schedule_id(self, employee_id: UUID, as_of: date) -> Optional[UUID]:
        """
        Resolve the schedule that applies on `as_of`: the active contract's
        override if one exists, otherwise the employee's default schedule.
        """
        async with httpx.AsyncClient(base_url=settings.HR_SERVICE_URL, timeout=10.0) as client:
            try:
                resp = await client.get(
                    "/api/v1/contracts/active",
                    params={"employee_id": str(employee_id), "as_of": as_of.isoformat()},
                    headers=self._headers,
                )
                if resp.status_code == 200:
                    schedule_id = resp.json().get("working_schedule_id")
                    if schedule_id:
                        return UUID(schedule_id)
            except httpx.RequestError:
                pass

            try:
                resp = await client.get(
                    f"/api/v1/employees/{employee_id}", headers=self._headers
                )
                if resp.status_code == 200:
                    schedule_id = resp.json().get("default_working_schedule_id")
                    if schedule_id:
                        return UUID(schedule_id)
            except httpx.RequestError:
                pass

        return None

    async def get_schedule_lines(self, schedule_id: UUID) -> list[dict]:
        async with httpx.AsyncClient(base_url=settings.HR_SERVICE_URL, timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"/api/v1/schedules/{schedule_id}", headers=self._headers
                )
                if resp.status_code == 200:
                    return resp.json().get("lines", [])
            except httpx.RequestError:
                pass
        return []
