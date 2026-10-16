"""
conftest.py — testlar uchun umumiy sozlama.
Testlar ASL bazaga tegmaydi: vaqtinchalik SQLite fayl ishlatiladi.
AI tokeni ataylab bo'sh qilinadi — shunda testlar internetsiz ham bir xil natija beradi (zaxira rejim).
"""
import os
import sys
import tempfile

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["HF_TOKEN"] = ""
os.environ["ADMIN_KEY"] = "test-key"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from database import Base, SessionLocal, engine  # noqa: E402
from main import app  # noqa: E402
from seed import seed_if_empty  # noqa: E402


@pytest.fixture()
def client():
    """Har bir test uchun toza baza: jadvallar qayta yaratiladi va 8 ta xona turi qo'shiladi."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_if_empty(db)
    db.close()
    with TestClient(app) as c:
        yield c
