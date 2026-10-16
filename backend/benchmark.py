"""
benchmark.py — saytning backend tezligini o'lchaydi.

Ishlatish:   python benchmark.py
Real mehmonxonaga yaqin hajmda sinov bazasi yaratadi (150 xona, 3000 bron, 1500 sharh),
so'ng asosiy API manzillarni 30 martadan chaqirib, vaqtni (millisekund) o'lchaydi.
Asl hotel.db fayliga TEGMAYDI — vaqtinchalik baza ishlatiladi.
"""
import os
import random
import statistics
import sys
import tempfile
import time
from datetime import date, timedelta

# Vaqtinchalik baza: asl bazaga tegmaslik uchun
tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{tmp.name}"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient  # noqa: E402

from database import Base, SessionLocal, engine  # noqa: E402
from main import app  # noqa: E402
from models import Booking, Review, Room  # noqa: E402

ROOMS, BOOKINGS, REVIEWS, RUNS = 150, 3000, 1500, 30


def fill_database():
    random.seed(1)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    types = [("standard", 45, 2), ("deluxe", 85, 3), ("family", 130, 5), ("suite", 240, 3)]
    for i in range(ROOMS):
        t, price, cap = random.choice(types)
        db.add(Room(name=f"{t.title()} {100 + i}", room_type=t, price_per_night=price + random.randint(0, 20),
                    capacity=cap, floor=1 + i // 15, description="Sinov xonasi",
                    amenities="wifi,tv,konditsioner,balkon" if i % 2 else "wifi,tv,nonushta"))
    db.commit()
    base = date.today()
    for _ in range(BOOKINGS):
        start = base + timedelta(days=random.randint(-30, 120))
        nights = random.randint(1, 6)
        db.add(Booking(room_id=random.randint(1, ROOMS), guest_name="Sinov Mehmon", guest_email="s@mail.com",
                       check_in=start, check_out=start + timedelta(days=nights), guests=2,
                       total_price=nights * 80, status=random.choice(["confirmed"] * 9 + ["cancelled"])))
    for _ in range(REVIEWS):
        db.add(Review(room_id=random.randint(1, ROOMS), author="Sinov", rating=random.randint(1, 5),
                      comment="Yaxshi xona", sentiment="positive", sentiment_score=0.5))
    db.commit()
    db.close()


def measure(client, name, method, url, **kw):
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        r = getattr(client, method)(url, **kw)
        times.append((time.perf_counter() - t0) * 1000)
        assert r.status_code == 200, (name, r.status_code, r.text[:200])
    times.sort()
    p50 = statistics.median(times)
    p95 = times[int(len(times) * 0.95) - 1]
    wire = int(r.headers.get("content-length", len(r.content)))   # tarmoqdan haqiqatda o'tgan hajm (siqilgan)
    print(f"{name:<46} o'rtacha {p50:7.1f} ms   p95 {p95:7.1f} ms   javob {len(r.content) / 1024:5.1f} KB -> tarmoqda {wire / 1024:5.1f} KB")
    return p50


if __name__ == "__main__":
    fill_database()
    in_a, out_a = date.today() + timedelta(days=10), date.today() + timedelta(days=13)
    with TestClient(app, headers={"Accept-Encoding": "gzip"}) as client:
        print(f"Sinov hajmi: {ROOMS} xona, {BOOKINGS} bron, {REVIEWS} sharh; har biri {RUNS} marta\n")
        measure(client, "GET  /api/rooms (sanasiz)", "get", "/api/rooms")
        measure(client, "GET  /api/rooms (sana bilan)", "get",
                f"/api/rooms?check_in={in_a}&check_out={out_a}&guests=2")
        measure(client, "POST /api/ai/recommend", "post", "/api/ai/recommend",
                json={"text": "2 kishi, balkonli, 100$ gacha", "check_in": str(in_a), "check_out": str(out_a)})
        measure(client, "GET  /api/admin/stats", "get", "/api/admin/stats", headers={"X-Admin-Key": "admin123"})
        measure(client, "GET  /api/admin/bookings", "get", "/api/admin/bookings", headers={"X-Admin-Key": "admin123"})
    os.unlink(tmp.name)
