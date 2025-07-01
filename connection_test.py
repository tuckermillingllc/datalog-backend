from dotenv import load_dotenv, dotenv_values
import os

print("dotenv_values():", dotenv_values())
load_dotenv()
print("os.getenv('DATABASE_URL'):", os.getenv("DATABASE_URL"))
