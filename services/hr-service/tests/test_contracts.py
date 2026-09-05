import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch
import pytest
from fastapi import HTTPException
from app.models.contract import Contract


@pytest.mark.asyncio
async def test_contracts_active_route_resolution(client, hr_manager_headers):
    """Ensure /api/v1/contracts/active is matched before /{contract_id} and does not error on path parsing."""
    emp_id = uuid.uuid4()
    mock_contract = Contract(
        id=uuid.uuid4(),
        employee_id=emp_id,
        contract_type="PERMANENT",
        start_date=date(2026, 1, 1),
        end_date=None,
        wage_amount=Decimal("50000.00"),
        wage_type="MONTHLY",
        salary_structure_id=uuid.uuid4(),
        status="ACTIVE",
        signed_date=date(2026, 1, 1),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch("app.services.contract_service.ContractService.get_active", new_callable=AsyncMock) as mock_active:
        mock_active.return_value = mock_contract
        response = await client.get(
            f"/api/v1/contracts/active?employee_id={emp_id}&as_of=2026-06-01",
            headers=hr_manager_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["employee_id"] == str(emp_id)
        assert data["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_get_active_contract_not_found_404(client, hr_manager_headers):
    emp_id = uuid.uuid4()
    with patch("app.services.contract_service.ContractService.get_active", new_callable=AsyncMock) as mock_active:
        mock_active.side_effect = HTTPException(status_code=404, detail="No active contract")
        response = await client.get(
            f"/api/v1/contracts/active?employee_id={emp_id}",
            headers=hr_manager_headers,
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_contract_as_payroll_user_forbidden(client, payroll_user_headers):
    payload = {
        "employee_id": str(uuid.uuid4()),
        "contract_type": "PERMANENT",
        "start_date": "2026-01-01",
        "wage_amount": "60000.00",
        "wage_type": "MONTHLY",
        "salary_structure_id": str(uuid.uuid4()),
    }
    response = await client.post("/api/v1/contracts/", json=payload, headers=payroll_user_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_contract_overlap_raises_409(client, hr_manager_headers):
    emp_id = uuid.uuid4()
    payload = {
        "employee_id": str(emp_id),
        "contract_type": "PERMANENT",
        "start_date": "2026-01-01",
        "wage_amount": "60000.00",
        "wage_type": "MONTHLY",
        "salary_structure_id": str(uuid.uuid4()),
    }
    with patch("app.services.contract_service.ContractService.create", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = HTTPException(
            status_code=409,
            detail="Contract dates overlap an existing ACTIVE contract for this employee.",
        )
        response = await client.post("/api/v1/contracts/", json=payload, headers=hr_manager_headers)
        assert response.status_code == 409
        assert "overlap" in response.json()["detail"].lower()
