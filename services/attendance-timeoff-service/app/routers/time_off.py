from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.time_off_type import TimeOffType
from app.models.time_off_request import TimeOffRequest
from app.schemas.time_off import (
    TimeOffTypeCreate, TimeOffTypeOut,
    TimeOffRequestCreate, TimeOffRequestOut
)

router = APIRouter(prefix="/time-off", tags=["Time Off"])

@router.get("/types", response_model=list[TimeOffTypeOut])
async def list_time_off_types(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TimeOffType))
    return result.scalars().all()

@router.post("/types", response_model=TimeOffTypeOut)
async def create_time_off_type(type_in: TimeOffTypeCreate, db: AsyncSession = Depends(get_db)):
    t = TimeOffType(**type_in.model_dump())
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t

@router.get("/requests", response_model=list[TimeOffRequestOut])
async def list_requests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TimeOffRequest))
    return result.scalars().all()

@router.post("/requests", response_model=TimeOffRequestOut)
async def create_request(req_in: TimeOffRequestCreate, db: AsyncSession = Depends(get_db)):
    req = TimeOffRequest(**req_in.model_dump())
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req
