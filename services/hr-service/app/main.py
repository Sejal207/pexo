from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import employees, departments, schedules, contracts

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json",
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(schedules.router)
app.include_router(contracts.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hr-service"}
