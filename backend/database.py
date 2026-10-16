"""
database.py — bazaga ulanish.

Lokal kompyuterda SQLite (oddiy fayl: hotel.db) ishlatiladi.
Railway'da esa DATABASE_URL (PostgreSQL) berilsa, o'sha ishlatiladi.
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hotel.db")

# Railway ba'zan "postgres://..." deb beradi, SQLAlchemy esa "postgresql://" kutadi
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite uchun qo'shimcha sozlama kerak, PostgreSQL uchun kerak emas
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """Har bir so'rov uchun alohida baza sessiyasi ochadi va oxirida yopadi."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
