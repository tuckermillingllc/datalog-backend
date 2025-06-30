from fastapi import FastAPI
from app.api.endpoints import logs, health

app = FastAPI()

app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
