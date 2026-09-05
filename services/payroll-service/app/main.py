from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import payruns, payslips, rules, structures

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(structures.router, prefix="/api/v1")
app.include_router(rules.router, prefix="/api/v1")
app.include_router(payruns.router, prefix="/api/v1")
app.include_router(payslips.router, prefix="/api/v1")


@app.get("/health")
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "payroll-service"}
