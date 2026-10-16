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

# Railway ba'zan "postgres://..." yoki "postgresql://..." deb beradi.
# Loyihada psycopg2 o'rnatilgan, shuning uchun drayverni aniq ko'rsatamiz
# (aks holda SQLAlchemy 2.1 "psycopg" (v3) ni qidiradi va xato beradi).
for _prefix in ("postgres://", "postgresql://"):
    if DATABASE_URL.startswith(_prefix):
        DATABASE_URL = "postgresql+psycopg2://" + DATABASE_URL[len(_prefix):]
        break

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
