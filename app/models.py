from sqlalchemy import Column, Integer, String, Text, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.database import Base

# Your existing model
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String, index=True)

class ContainerLogPrepupae(Base):
    __tablename__ = "container_logs_prepupae"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    datetime = Column(DateTime, default=func.now())
    temperature = Column(DECIMAL(5, 2))
    humidity = Column(DECIMAL(5, 2))
    prepupae_tubs_added = Column(Integer)
    egg_nests_replaced = Column(Integer)
    notes = Column(Text)

class ContainerLogNeonates(Base):
    __tablename__ = "container_logs_neonates"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    datetime = Column(DateTime, default=func.now())
    temperature = Column(DECIMAL(5, 2))
    humidity = Column(DECIMAL(5, 2))
    bait_tubs_replaced = Column(Integer)
    shelf_tubs_removed = Column(Integer)
    egg_nests_replaced = Column(Integer)
    notes = Column(Text)

class MicrowaveLog(Base):
    __tablename__ = "microwave_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    datetime = Column(DateTime, default=func.now())
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

# Your existing Log model is already defined above