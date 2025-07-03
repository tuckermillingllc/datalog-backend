from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, DECIMAL
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
    allow_origins=[
        "https://datalog-frontend.onrender.com",
        "https://datalog-frontend.onrender.com/",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
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
    post_feed_condition = Column(String(50), nullable=True)


class ContainerLogPrepupae(Base):
    __tablename__ = "container_logs_prepupae"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    username = Column(String(100), nullable=False)
    temperature = Column(DECIMAL(5, 2))
    humidity = Column(DECIMAL(5, 2))
    prepupae_tubs_added = Column(Integer)
    egg_nests_replaced = Column(Integer)
    notes = Column(Text)

class ContainerLogNeonates(Base):
    __tablename__ = "container_logs_neonates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    username = Column(String(100), nullable=False)
    temperature = Column(DECIMAL(5, 2))
    humidity = Column(DECIMAL(5, 2))
    bait_tubs_replaced = Column(Integer)
    shelf_tubs_removed = Column(Integer)
    egg_nests_replaced = Column(Integer)
    notes = Column(Text)

class MicrowaveLog(Base):
    __tablename__ = "microwave_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    username = Column(String(100), nullable=False)
    microwave_power_gen1 = Column(DECIMAL(5, 2))
    microwave_power_gen2 = Column(DECIMAL(5, 2))
    fan_speed_cavity1 = Column(DECIMAL(5, 2))
    fan_speed_cavity2 = Column(DECIMAL(5, 2))
    belt_speed = Column(DECIMAL(5, 2))
    lb_larvae_per_tub = Column(DECIMAL(6, 2))
    num_ramp_up_tubs = Column(Integer)
    num_ramp_down_tubs = Column(Integer)
    # Post-production fields (nullable)
    tubs_live_larvae = Column(Integer, nullable=True)
    lb_dried_larvae = Column(DECIMAL(6, 2), nullable=True)
    yield_percentage = Column(DECIMAL(5, 2), nullable=True)
    notes = Column(Text)

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
            "larvae_logs": "GET/POST/PUT /api/logs",
            "container_prepupae": "GET/POST /api/container-logs/prepupae",
            "container_neonates": "GET/POST /api/container-logs/neonates",
            "microwave_logs": "GET/POST/PUT /api/microwave-logs",
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

# ============ LARVAE LOGS (existing) ============

# Create larvae log
@app.post("/api/logs")
async def create_log(data: Dict[str, Any], db: Session = Depends(get_db)):
    required_fields = ["username", "days_of_age", "larva_weight", "larva_pct", 
                       "lb_larvae", "lb_feed", "lb_water"]

    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

    try:
        larva_weight = float(data["larva_weight"])
        larva_pct = float(data["larva_pct"])
        lb_larvae = float(data["lb_larvae"])
        lb_feed = float(data["lb_feed"])
        lb_water = float(data["lb_water"])

        larvae_count = int(((lb_larvae * (larva_pct / 100)) * 453592) / larva_weight) if larva_weight > 0 else 0
        feed_per_larvae = round((lb_feed * 453592) / larvae_count, 1) if larvae_count > 0 else 0
        water_feed_ratio = round(lb_water / lb_feed, 1) if lb_feed > 0 else 0

        log = LarvaeLog(
            username=data["username"],
            days_of_age=int(data["days_of_age"]),
            larva_weight=int(larva_weight),
            larva_pct=int(larva_pct),
            lb_larvae=int(lb_larvae),
            lb_feed=lb_feed,
            lb_water=lb_water,
            screen_refeed=data.get("screen_refeed", False),
            row_number=data.get("row_number"),
            notes=data.get("notes"),
            post_feed_condition=data.get("post_feed_condition"),  # <-- NEW
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
            "post_feed_condition": log.post_feed_condition,  # <-- NEW
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
    username: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LarvaeLog)

    if username:
        query = query.filter(LarvaeLog.username == username)

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
        "post_feed_condition": log.post_feed_condition,  # <-- NEW
        "larvae_count": log.larvae_count,
        "feed_per_larvae": log.feed_per_larvae,
        "water_feed_ratio": log.water_feed_ratio
    } for log in logs]


# Get single larvae log by ID
@app.get("/api/logs/{log_id}")
async def get_log(log_id: str, db: Session = Depends(get_db)):
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
            "post_feed_condition": log.post_feed_condition,  # <-- NEW
            "larvae_count": log.larvae_count,
            "feed_per_larvae": log.feed_per_larvae,
            "water_feed_ratio": log.water_feed_ratio
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")


# Delete larvae log by ID
@app.delete("/api/logs/{log_id}", status_code=204)
async def delete_log(log_id: str, db: Session = Depends(get_db)):
    try:
        log = db.query(LarvaeLog).filter(LarvaeLog.id == uuid.UUID(log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")

        db.delete(log)
        db.commit()
        return
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting log: {str(e)}")

# ============ CONTAINER LOGS - PREPUPAE ============

@app.get("/api/container-logs/prepupae")
async def get_container_logs_prepupae(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ContainerLogPrepupae)
    
    if username:
        query = query.filter(ContainerLogPrepupae.username == username)
    
    logs = query.order_by(ContainerLogPrepupae.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": str(log.id),
        "timestamp": log.timestamp.isoformat(),
        "username": log.username,
        "temperature": float(log.temperature) if log.temperature else None,
        "humidity": float(log.humidity) if log.humidity else None,
        "prepupae_tubs_added": log.prepupae_tubs_added,
        "egg_nests_replaced": log.egg_nests_replaced,
        "notes": log.notes
    } for log in logs]

@app.post("/api/container-logs/prepupae")
async def create_container_log_prepupae(data: Dict[str, Any], db: Session = Depends(get_db)):
    required_fields = ["username"]
    
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    try:
        log = ContainerLogPrepupae(
            username=data["username"],
            temperature=float(data["temperature"]) if data.get("temperature") else None,
            humidity=float(data["humidity"]) if data.get("humidity") else None,
            prepupae_tubs_added=int(data["prepupae_tubs_added"]) if data.get("prepupae_tubs_added") else None,
            egg_nests_replaced=int(data["egg_nests_replaced"]) if data.get("egg_nests_replaced") else None,
            notes=data.get("notes")
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat(),
            "username": log.username,
            "temperature": float(log.temperature) if log.temperature else None,
            "humidity": float(log.humidity) if log.humidity else None,
            "prepupae_tubs_added": log.prepupae_tubs_added,
            "egg_nests_replaced": log.egg_nests_replaced,
            "notes": log.notes
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating log: {str(e)}")

@app.delete("/api/container-logs/prepupae/{log_id}", status_code=204)
async def delete_container_log_prepupae(log_id: str, db: Session = Depends(get_db)):
    try:
        log = db.query(ContainerLogPrepupae).filter(ContainerLogPrepupae.id == uuid.UUID(log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")

        db.delete(log)
        db.commit()
        return
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting log: {str(e)}")

# ============ CONTAINER LOGS - NEONATES ============

@app.get("/api/container-logs/neonates")
async def get_container_logs_neonates(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ContainerLogNeonates)
    
    if username:
        query = query.filter(ContainerLogNeonates.username == username)
    
    logs = query.order_by(ContainerLogNeonates.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": str(log.id),
        "timestamp": log.timestamp.isoformat(),
        "username": log.username,
        "temperature": float(log.temperature) if log.temperature else None,
        "humidity": float(log.humidity) if log.humidity else None,
        "bait_tubs_replaced": log.bait_tubs_replaced,
        "shelf_tubs_removed": log.shelf_tubs_removed,
        "egg_nests_replaced": log.egg_nests_replaced,
        "notes": log.notes
    } for log in logs]

@app.post("/api/container-logs/neonates")
async def create_container_log_neonates(data: Dict[str, Any], db: Session = Depends(get_db)):
    required_fields = ["username"]
    
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    try:
        log = ContainerLogNeonates(
            username=data["username"],
            temperature=float(data["temperature"]) if data.get("temperature") else None,
            humidity=float(data["humidity"]) if data.get("humidity") else None,
            bait_tubs_replaced=int(data["bait_tubs_replaced"]) if data.get("bait_tubs_replaced") else None,
            shelf_tubs_removed=int(data["shelf_tubs_removed"]) if data.get("shelf_tubs_removed") else None,
            egg_nests_replaced=int(data["egg_nests_replaced"]) if data.get("egg_nests_replaced") else None,
            notes=data.get("notes")
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat(),
            "username": log.username,
            "temperature": float(log.temperature) if log.temperature else None,
            "humidity": float(log.humidity) if log.humidity else None,
            "bait_tubs_replaced": log.bait_tubs_replaced,
            "shelf_tubs_removed": log.shelf_tubs_removed,
            "egg_nests_replaced": log.egg_nests_replaced,
            "notes": log.notes
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating log: {str(e)}")

@app.delete("/api/container-logs/neonates/{log_id}", status_code=204)
async def delete_container_log_neonates(log_id: str, db: Session = Depends(get_db)):
    try:
        log = db.query(ContainerLogNeonates).filter(ContainerLogNeonates.id == uuid.UUID(log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")

        db.delete(log)
        db.commit()
        return
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting log: {str(e)}")

# ============ MICROWAVE LOGS ============

@app.get("/api/microwave-logs")
async def get_microwave_logs(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(MicrowaveLog)
    
    if username:
        query = query.filter(MicrowaveLog.username == username)
    
    logs = query.order_by(MicrowaveLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [{
        "id": str(log.id),
        "timestamp": log.timestamp.isoformat(),
        "username": log.username,
        "microwave_power_gen1": float(log.microwave_power_gen1) if log.microwave_power_gen1 else None,
        "microwave_power_gen2": float(log.microwave_power_gen2) if log.microwave_power_gen2 else None,
        "fan_speed_cavity1": float(log.fan_speed_cavity1) if log.fan_speed_cavity1 else None,
        "fan_speed_cavity2": float(log.fan_speed_cavity2) if log.fan_speed_cavity2 else None,
        "belt_speed": float(log.belt_speed) if log.belt_speed else None,
        "lb_larvae_per_tub": float(log.lb_larvae_per_tub) if log.lb_larvae_per_tub else None,
        "num_ramp_up_tubs": log.num_ramp_up_tubs,
        "num_ramp_down_tubs": log.num_ramp_down_tubs,
        "tubs_live_larvae": log.tubs_live_larvae,
        "lb_dried_larvae": float(log.lb_dried_larvae) if log.lb_dried_larvae else None,
        "yield_percentage": float(log.yield_percentage) if log.yield_percentage else None,
        "notes": log.notes
    } for log in logs]

@app.post("/api/microwave-logs")
async def create_microwave_log(data: Dict[str, Any], db: Session = Depends(get_db)):
    required_fields = ["username"]
    
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
    
    try:
        log = MicrowaveLog(
            username=data["username"],
            microwave_power_gen1=float(data["microwave_power_gen1"]) if data.get("microwave_power_gen1") else None,
            microwave_power_gen2=float(data["microwave_power_gen2"]) if data.get("microwave_power_gen2") else None,
            fan_speed_cavity1=float(data["fan_speed_cavity1"]) if data.get("fan_speed_cavity1") else None,
            fan_speed_cavity2=float(data["fan_speed_cavity2"]) if data.get("fan_speed_cavity2") else None,
            belt_speed=float(data["belt_speed"]) if data.get("belt_speed") else None,
            lb_larvae_per_tub=float(data["lb_larvae_per_tub"]) if data.get("lb_larvae_per_tub") else None,
            num_ramp_up_tubs=int(data["num_ramp_up_tubs"]) if data.get("num_ramp_up_tubs") else None,
            num_ramp_down_tubs=int(data["num_ramp_down_tubs"]) if data.get("num_ramp_down_tubs") else None,
            notes=data.get("notes")
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat(),
            "username": log.username,
            "microwave_power_gen1": float(log.microwave_power_gen1) if log.microwave_power_gen1 else None,
            "microwave_power_gen2": float(log.microwave_power_gen2) if log.microwave_power_gen2 else None,
            "fan_speed_cavity1": float(log.fan_speed_cavity1) if log.fan_speed_cavity1 else None,
            "fan_speed_cavity2": float(log.fan_speed_cavity2) if log.fan_speed_cavity2 else None,
            "belt_speed": float(log.belt_speed) if log.belt_speed else None,
            "lb_larvae_per_tub": float(log.lb_larvae_per_tub) if log.lb_larvae_per_tub else None,
            "num_ramp_up_tubs": log.num_ramp_up_tubs,
            "num_ramp_down_tubs": log.num_ramp_down_tubs,
            "tubs_live_larvae": log.tubs_live_larvae,
            "lb_dried_larvae": float(log.lb_dried_larvae) if log.lb_dried_larvae else None,
            "yield_percentage": float(log.yield_percentage) if log.yield_percentage else None,
            "notes": log.notes
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating log: {str(e)}")

@app.put("/api/microwave-logs/{log_id}")
async def update_microwave_log(log_id: str, data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        log = db.query(MicrowaveLog).filter(MicrowaveLog.id == uuid.UUID(log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        
        # Update post-production fields
        if "tubs_live_larvae" in data:
            log.tubs_live_larvae = int(data["tubs_live_larvae"]) if data["tubs_live_larvae"] else None
        if "lb_dried_larvae" in data:
            log.lb_dried_larvae = float(data["lb_dried_larvae"]) if data["lb_dried_larvae"] else None
        if "notes" in data:
            log.notes = data["notes"]
        
        # Calculate yield if we have the necessary data
        if (log.tubs_live_larvae and log.lb_dried_larvae and 
            log.lb_larvae_per_tub and log.tubs_live_larvae > 0 and log.lb_larvae_per_tub > 0):
            total_larvae_lbs = float(log.tubs_live_larvae) * float(log.lb_larvae_per_tub)
            log.yield_percentage = (float(log.lb_dried_larvae) / total_larvae_lbs) * 100
        
        db.commit()
        db.refresh(log)
        
        return {
            "id": str(log.id),
            "timestamp": log.timestamp.isoformat(),
            "username": log.username,
            "microwave_power_gen1": float(log.microwave_power_gen1) if log.microwave_power_gen1 else None,
            "microwave_power_gen2": float(log.microwave_power_gen2) if log.microwave_power_gen2 else None,
            "fan_speed_cavity1": float(log.fan_speed_cavity1) if log.fan_speed_cavity1 else None,
            "fan_speed_cavity2": float(log.fan_speed_cavity2) if log.fan_speed_cavity2 else None,
            "belt_speed": float(log.belt_speed) if log.belt_speed else None,
            "lb_larvae_per_tub": float(log.lb_larvae_per_tub) if log.lb_larvae_per_tub else None,
            "num_ramp_up_tubs": log.num_ramp_up_tubs,
            "num_ramp_down_tubs": log.num_ramp_down_tubs,
            "tubs_live_larvae": log.tubs_live_larvae,
            "lb_dried_larvae": float(log.lb_dried_larvae) if log.lb_dried_larvae else None,
            "yield_percentage": float(log.yield_percentage) if log.yield_percentage else None,
            "notes": log.notes
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating log: {str(e)}")

@app.delete("/api/microwave-logs/{log_id}", status_code=204)
async def delete_microwave_log(log_id: str, db: Session = Depends(get_db)):
    try:
        log = db.query(MicrowaveLog).filter(MicrowaveLog.id == uuid.UUID(log_id)).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")

        db.delete(log)
        db.commit()
        return
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting log: {str(e)}")