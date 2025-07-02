from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import uuid

# FastAPI app
app = FastAPI(title="DataLog API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
else:
    print("WARNING: No DATABASE_URL found")
    engine = None
    SessionLocal = None

Base = declarative_base()

# Models
class LarvaeLog(Base):
    __tablename__ = "larvae_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    username = Column(String(100), nullable=False)
    days_of_age = Column(Integer, nullable=False)
    larva_weight = Column(Integer, nullable=False)
    larva_pct = Column(Integer, nullable=False)
    lb_larvae = Column(Integer, nullable=False)
    lb_feed = Column(Float, nullable=False)
    lb_water = Column(Float, nullable=False)
    screen_refeed = Column(Boolean, default=False)
    row_number = Column(String(50))
    notes = Column(Text)
    larvae_count = Column(Integer)
    feed_per_larvae = Column(Float)
    water_feed_ratio = Column(Float)

# Create tables if engine exists
if engine:
    Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    if not SessionLocal:
        raise HTTPException(status_code=500, detail="Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "DataLog API", 
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "create_log": "POST /api/logs",
            "get_logs": "GET /api/logs",
            "api_docs": "/docs"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# API Health check
@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "api_version": "1.0.0"}

# Create larvae log
@app.post("/api/logs")
async def create_log(data: Dict[str, Any]):
    db = next(get_db())
    
    # Validate required fields
    required_fields = ["username", "days_of_age", "larva_weight", "larva_pct", 
                      "lb_larvae", "lb_feed", "lb_water"]
    
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    try:
        # Extract values
        larva_weight = float(data["larva_weight"])
        larva_pct = float(data["larva_pct"])
        lb_larvae = float(data["lb_larvae"])
        lb_feed = float(data["lb_feed"])
        lb_water = float(data["lb_water"])
        
        # Calculate derived fields
        larvae_count = int(((lb_larvae * (larva_pct / 100)) * 453592) / larva_weight) if larva_weight > 0 else 0
        feed_per_larvae = round((lb_feed * 453592) / larvae_count, 1) if larvae_count > 0 else 0
        water_feed_ratio = round(lb_water / lb_feed, 1) if lb_feed > 0 else 0
        
        # Create log entry
        log = LarvaeLog(
            username=data["username"],
            days_of_age=int(data["days_of_age"]),
            larva_weight=int(larva_weight),
            larva_pct=int(larva_pct),
            lb_larvae=int(lb_larvae),
            lb_feed=lb_feed,
            lb_water=lb_water,
            screen_refeed=data.get("screen_refeed", False),
            row_number=data.get("row_number"),  # FIXED: Changed from "tub_color"
            notes=data.get("notes"),
            larvae_count=larvae_count,
            feed_per_larvae=feed_per_larvae,
            water_feed_ratio=water_feed_ratio
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat(),
            "username": log.username,
            "days_of_age": log.days_of_age,
            "larva_weight": log.larva_weight,
            "larva_pct": log.larva_pct,
            "lb_larvae": log.lb_larvae,
            "lb_feed": log.lb_feed,
            "lb_water": log.lb_water,
            "screen_refeed": log.screen_refeed,
            "row_number": log.row_number,
            "notes": log.notes,
            "larvae_count": log.larvae_count,
            "feed_per_larvae": log.feed_per_larvae,
            "water_feed_ratio": log.water_feed_ratio
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating log: {str(e)}")

# Get larvae logs
@app.get("/api/logs")
async def get_logs(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None  # FIXED: Changed from user
):
    db = next(get_db())
    
    query = db.query(LarvaeLog)
    
    if username:  # FIXED: Changed from user
        query = query.filter(LarvaeLog.username == username)  # FIXED: Changed from LarvaeLog.user == user
    
    logs = query.order_by(LarvaeLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": str(log.id),
        "timestamp": log.timestamp.isoformat(),
        "username": log.username,
        "days_of_age": log.days_of_age,
        "larva_weight": log.larva_weight,
        "larva_pct": log.larva_pct,
        "lb_larvae": log.lb_larvae,
        "lb_feed": log.lb_feed,
        "lb_water": log.lb_water,
        "screen_refeed": log.screen_refeed,
        "row_number": log.row_number,
        "notes": log.notes,
        "larvae_count": log.larvae_count,
        "feed_per_larvae": log.feed_per_larvae,
        "water_feed_ratio": log.water_feed_ratio
    } for log in logs]

# Get single log by ID
@app.get("/api/logs/{log_id}")
async def get_log(log_id: str):
    db = next(get_db())
    
    try:
        log = db.query(LarvaeLog).filter(LarvaeLog.id == uuid.UUID(log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        
        return {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat(),
            "username": log.username,
            "days_of_age": log.days_of_age,
            "larva_weight": log.larva_weight,
            "larva_pct": log.larva_pct,
            "lb_larvae": log.lb_larvae,
            "lb_feed": log.lb_feed,
            "lb_water": log.lb_water,
            "screen_refeed": log.screen_refeed,
            "row_number": log.row_number,
            "notes": log.notes,
            "larvae_count": log.larvae_count,
            "feed_per_larvae": log.feed_per_larvae,
            "water_feed_ratio": log.water_feed_ratio
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

# Delete a log by ID
@app.delete("/api/logs/{log_id}", status_code=204)
async def delete_log(log_id: str):
    db = next(get_db())
    
    try:
        log = db.query(LarvaeLog).filter(LarvaeLog.id == uuid.UUID(log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")

        db.delete(log)
        db.commit()
        return  # 204 No Content
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting log: {str(e)}")
