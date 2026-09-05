import uuid
from datetime import datetime, timezone, time
from unittest.mock import AsyncMock, patch
import pytest
from app.models.working_schedule import WorkingSchedule, WorkingScheduleLine


@pytest.mark.asyncio
async def test_list_schedules(client, hr_manager_headers):
    sched_id = uuid.uuid4()
    mock_sched = WorkingSchedule(
        id=sched_id,
        name="Standard 40h",
        schedule_type="FULL_TIME",
        total_weekly_hours=40.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    with patch("app.services.working_schedule_service.WorkingScheduleService.get_all", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = [mock_sched]
        response = await client.get("/api/v1/schedules/", headers=hr_manager_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Standard 40h"


@pytest.mark.asyncio
async def test_create_schedule_with_lines(client, hr_manager_headers):
    sched_id = uuid.uuid4()
    mock_sched = WorkingSchedule(
        id=sched_id,
        name="Standard 40h",
        schedule_type="FULL_TIME",
        total_weekly_hours=40.0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        lines=[
            WorkingScheduleLine(
                id=uuid.uuid4(),
                working_schedule_id=sched_id,
                day="MON",
                start_time=time(9, 0),
                end_time=time(17, 0),
                break_minutes=60,
            )
        ],
    )
    with patch("app.services.working_schedule_service.WorkingScheduleService.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_sched
        payload = {
            "name": "Standard 40h",
            "schedule_type": "FULL_TIME",
            "lines": [
                {
                    "day": "MON",
                    "start_time": "09:00:00",
                    "end_time": "17:00:00",
                    "break_minutes": 60,
                }
            ],
        }
        response = await client.post("/api/v1/schedules/", json=payload, headers=hr_manager_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Standard 40h"
        assert len(data["lines"]) == 1
        assert data["lines"][0]["day"] == "MON"
