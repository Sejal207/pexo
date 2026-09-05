from fastapi import APIRouter, Depends
import redis.asyncio as redis
from app.core.redis_client import get_redis_client
from app.dashboard.aggregator import DashboardAggregator

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/kpis")
async def get_dashboard_kpis(r_client: redis.Redis = Depends(get_redis_client)):
    aggregator = DashboardAggregator(r_client)
    return await aggregator.get_kpis()
