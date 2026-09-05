"""
Thin HTTP client to hr-service. Used by:
- the payrun wizard (Pipeline 4) to resolve the eligible-employee set for a
  period, forwarding the original caller's bearer token;
- the rule engine + validate workflow (Pipeline 5), which run from a Celery
  task or an HTTP handler and need a contract's wage, an employee's name, and
  bank-account presence. Background tasks have no caller token, so those call
  sites pass a minted service token instead (see core/security.mint_service_token).
"""
from datetime import date
from typing import Optional
from uuid import UUID

import httpx
from fastapi import HTTPException

from app.core.config import settings


class HRClient:
    def __init__(self, bearer_token: str) -> None:
        self._headers = {"Authorization": f"Bearer {bearer_token}"}

    async def _get(self, path: str, *, params: Optional[dict] = None) -> dict | list:
        async with httpx.AsyncClient(base_url=settings.HR_SERVICE_URL, timeout=10.0) as client:
            try:
                resp = await client.get(path, params=params, headers=self._headers)
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=502, detail=f"hr-service unreachable: {exc}"
                ) from exc

        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"hr-service: not found ({path})")
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code if resp.status_code in (401, 403) else 502,
                detail=f"hr-service call to {path} failed: {resp.text}",
            )
        return resp.json()

    async def list_eligible_contracts(
        self,
        *,
        period_start: date,
        period_end: date,
        salary_structure_id: UUID,
        department_id: Optional[UUID] = None,
        contract_type: Optional[str] = None,
    ) -> list[dict]:
        params: dict[str, str] = {
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "salary_structure_id": str(salary_structure_id),
        }
        if department_id:
            params["department_id"] = str(department_id)
        if contract_type:
            params["contract_type"] = contract_type
        return await self._get("/api/v1/contracts/eligible", params=params)  # type: ignore[return-value]

    async def get_contract(self, contract_id: UUID) -> dict:
        return await self._get(f"/api/v1/contracts/{contract_id}")  # type: ignore[return-value]

    async def get_employee(self, employee_id: UUID) -> dict:
        return await self._get(f"/api/v1/employees/{employee_id}")  # type: ignore[return-value]

    async def has_primary_bank_account(self, employee_id: UUID) -> bool:
        accounts = await self._get(f"/api/v1/employees/{employee_id}/bank-accounts")
        return bool(accounts)
