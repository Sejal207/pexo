import httpx

from app.core.config import settings


class PayrollClient:
    def __init__(self):
        self.base_url = settings.PAYROLL_SERVICE_URL

    async def get_payruns(self):
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            resp = await client.get("/payruns/")
            resp.raise_for_status()
            return resp.json()
