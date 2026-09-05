import httpx
from app.core.config import settings

class HRClient:
    def __init__(self):
        self.base_url = settings.HR_SERVICE_URL

    async def get_employees(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            resp = await client.get("/employees/")
            resp.raise_for_status()
            return resp.json()
