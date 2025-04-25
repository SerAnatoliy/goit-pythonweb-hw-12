import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter

load_dotenv()

print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

if SQLALCHEMY_DATABASE_URL is None:
    print("ERROR: DATABASE_URL is not set.")
else:
    print(f"Using database: {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from app.database import models

async def init_limiter():
    redis = await aioredis.from_url(REDIS_URL)
    await FastAPILimiter.init(redis)

AVATAR_STORAGE_PATH = os.getenv("AVATAR_STORAGE_PATH", "app/static/avatars")

os.makedirs(AVATAR_STORAGE_PATH, exist_ok=True)