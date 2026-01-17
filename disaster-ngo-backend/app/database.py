from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Render / production uses ENV variables, NOT .env files
DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL USED BY BACKEND:", DATABASE_URL)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(
    DATABASE_URL,
    echo=False   # turn off SQL logs in production
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
