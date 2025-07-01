import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

print("All environment variables with dpg:")
for k, v in os.environ.items():
    if "dpg" in v:
        print(f"{k}={v}")

# Get the DATABASE_URL from the .env file
DATABASE_URL = os.getenv("DATABASE_URL")

print("Loaded DATABASE_URL:", DATABASE_URL)

# Raise error early if missing
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your .env file or dotenv loading.")

# Create engine with appropriate options
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# Setup session and base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
