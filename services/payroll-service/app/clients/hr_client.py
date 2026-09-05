from datetime import date
from typing import Optional
from uuid import UUID

import httpx

from app.core.config import settings


class HRClient:
    def __init__(self, bearer_token: str) -> None:
        self._headers = {"Authorization": "Bearer " + bearer_token}

    async def list_eligible_contracts(
        self,
        *,
        period_start: date,
        period_end: date,
        salary_structure_id: UUID,
        department_id: Optional[UUID] = None,
        contract_type: Optional[str] = None,
    ) -> list[dict]:
        params = {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "salary_structure_id": str(salary_structure_id),
        }
        if department_id is not None:
            params["department_id"] = str(department_id)
        if contract_type is not None:
            params["contract_type"] = contract_type

        async with httpx.AsyncClient(base_url=settings.HR_SERVICE_URL, timeout=10.0) as client:
            response = await client.get(
                "/api/v1/contracts/eligible",
                params=params,
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()

    async def get_employee(self, employee_id: UUID) -> dict:
        async with httpx.AsyncClient(base_url=settings.HR_SERVICE_URL, timeout=10.0) as client:
            response = await client.get(
                f"/api/v1/employees/{employee_id}",
                headers=self._headers,
            )
            response.raise_for_status()
            return response.json()
