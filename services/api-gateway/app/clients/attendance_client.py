import httpx
from app.core.config import settings

class AttendanceClient:
    def __init__(self):
        self.base_url = settings.ATTENDANCE_SERVICE_URL

    async def get_attendance(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            resp = await client.get("/attendance/")
            resp.raise_for_status()
            return resp.json()
