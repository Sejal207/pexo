import json
import redis.asyncio as redis
from app.clients.hr_client import HRClient
from app.clients.payroll_client import PayrollClient

class DashboardAggregator:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.hr = HRClient()
        self.payroll = PayrollClient()

    async def get_kpis(self) -> dict:
        cached = await self.redis.get("dashboard_kpis")
        if cached:
            return json.loads(cached)

        # Fallback to live query
        try:
            employees = await self.hr.get_employees()
            payruns = await self.payroll.get_payruns()
            kpis = {
                "total_employees": len(employees),
                "active_payruns": len([p for p in payruns if p.get("status") == "DRAFT"]),
                "last_updated": "live"
            }
            await self.redis.setex("dashboard_kpis", 300, json.dumps(kpis))
            return kpis
        except Exception:
            return {"total_employees": 0, "active_payruns": 0, "status": "unavailable"}
