from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import logs, health

app = FastAPI()

# 🔥 Add this CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 In production, use your frontend domain here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
