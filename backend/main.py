"""
main.py — backendning asosiy fayli (FastAPI): BARCHA API manzillar (endpointlar) shu yerda.

Ishga tushirish:  uvicorn main:app --reload
Avtomatik hujjat (Swagger): http://127.0.0.1:8000/docs

Manzillar:
  GET  /api/health                  — server va AI holati
  GET  /api/hotel                   — mehmonxona profili: bino, qavatlar, xodimlar, qulayliklar, hujjatlar
  GET  /api/rooms, /api/rooms/{id}  — xonalar (filtr: tur, narx, mehmonlar, sanalar, kimlar uchun)
  GET  /api/rooms/{id}/reviews      — sharhlar
  POST /api/bookings, GET /api/bookings?email=, POST /api/bookings/{id}/cancel — bron
  POST /api/reviews                 — sharh (AI kayfiyatni aniqlaydi)
  POST /api/ai/chat, /api/ai/recommend — AI yordamchi va AI qidiruv
  GET  /api/admin/stats, /api/admin/bookings — admin (X-Admin-Key kerak)
Qoidalar (band-bo'shlik, narx) services.py da, AI ai.py da, ma'lumot hotel_info.py da.
"""
import os
import time
from contextlib import asynccontextmanager
from datetime import date, timedelta
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import func, inspect
from sqlalchemy.orm import Session, joinedload

import ai
import chatbot
import hotel_info
import schemas
from database import Base, SessionLocal, engine, get_db
from models import Booking, Review, Room
from seed import seed_if_empty, sync_room_display
from services import calc_total, is_room_available, rank_rooms, room_to_dict, rooms_to_dicts

ADMIN_KEY = os.getenv("ADMIN_KEY", "admin123")

# Real mehmonxona qoidalari
MAX_NIGHTS = 30            # bir bronda eng ko'pi bilan 30 kecha
MAX_DAYS_AHEAD = 365       # bronni eng ko'pi bilan 1 yil oldin qilish mumkin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Server yoqilganda bir marta ishlaydi: jadvallarni yaratadi va boshlang'ich xonalarni qo'shadi."""
    inspector = inspect(engine)
    stale = (inspector.has_table("rooms") and ("code" not in [c["name"] for c in inspector.get_columns("rooms")] or "images" not in [c["name"] for c in inspector.get_columns("rooms")])) or \
            (inspector.has_table("bookings") and "doc_type" not in [c["name"] for c in inspector.get_columns("bookings")])
    if stale:
        # Baza eski versiyadan qolgan: yangi ustunlar yo'q. Ma'lumotni jimgina o'chirmaymiz — aniq xabar beramiz.
        raise RuntimeError("Baza eski versiyada. hotel.db faylini o'chirib, serverni qayta ishga tushiring "
                           "(PostgreSQL bo'lsa, jadvallarni qayta yarating).")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
        sync_room_display(db)      # nom/tavsif/suratlar o'zgargan bo'lsa, eski bazaga ham ko'chiradi
    finally:
        db.close()
    yield


app = FastAPI(title="Silk Road Grand Hotel — Bron tizimi (AI bilan)", lifespan=lifespan)

# Javobni siqish (gzip): xonalar ro'yxati ~35 KB dan ~5 KB gacha kichrayadi => sayt tezroq ochiladi
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS: Netlify'dagi sayt (boshqa domen) backendga murojaat qila olishi uchun
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])


@app.middleware("http")
async def add_process_time(request, call_next):
    """Har bir javobga "X-Process-Time" (millisekund) sarlavhasini qo'shadi — tezlikni o'lchash uchun."""
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{(time.perf_counter() - start) * 1000:.1f}ms"
    return response


def require_admin(x_admin_key: str = Header(default="")):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Admin kaliti noto'g'ri")


def booking_to_out(b: Booking) -> dict:
    return {
        "id": b.id, "code": f"SR-{b.created_at.year}-{b.id:05d}", "room_id": b.room_id, "room_name": b.room.name,
        "guest_name": b.guest_name, "guest_email": b.guest_email, "guest_phone": b.guest_phone,
        "check_in": b.check_in, "check_out": b.check_out, "guests": b.guests,
        "total_price": b.total_price, "status": b.status, "created_at": b.created_at,
        "doc_type": b.doc_type or None,
        "doc_number_masked": ("•" * 4 + b.doc_number[-3:]) if b.doc_number else None,   # to'liq raqam qaytarilmaydi
        "is_couple": bool(b.is_couple),
    }


# ----------------------------------------------------------------------------
# Umumiy
# ----------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "ai_enabled": ai.ai_enabled(), "model": ai.HF_MODEL if ai.ai_enabled() else None}


# ----------------------------------------------------------------------------
# Mehmonxona haqida (profil, qulayliklar, hujjatlar, joylashuv)
# ----------------------------------------------------------------------------
def _floors_with_room_types(db: Session) -> list:
    """Har bir qavatga u yerdagi xona turlarini qo'shadi (bazadagi `floors` maydoni: "3–6" yoki "9")."""
    rooms = db.query(Room).all()
    result = []
    for f in hotel_info.FLOORS:
        types = []
        for r in rooms:
            parts = [int(x) for x in str(r.floors).replace("–", "-").split("-") if x.strip().isdigit()]
            if parts and parts[0] <= f["floor"] <= parts[-1]:
                types.append({"id": r.id, "code": r.code, "name": r.name, "price": r.price_per_night})
        result.append({**f, "room_types": types})
    return result


@app.get("/api/hotel")
def hotel_profile(db: Session = Depends(get_db)):
    """Sayt "Mehmonxona haqida", "Qulayliklar", "Hujjatlar" bo'limlarini shu ma'lumotdan chizadi."""
    rooms_total = db.query(func.coalesce(func.sum(Room.quantity), 0)).scalar()
    return {
        **hotel_info.HOTEL,
        "rooms_total": int(rooms_total),
        "room_types": db.query(Room).count(),
        "layout": hotel_info.LAYOUT,
        "floors": _floors_with_room_types(db),
        "entrance": hotel_info.ENTRANCE,
        "staff": hotel_info.STAFF,
        "distances": hotel_info.DISTANCES,
        "facilities": hotel_info.FACILITIES,
        "documents": hotel_info.DOCUMENTS,
        "policies": hotel_info.POLICIES,
        "audiences": hotel_info.AUDIENCES,
        "photo_credits": hotel_info.PHOTO_CREDITS,
        "gallery": hotel_info.GALLERY,
        "welcome": hotel_info.WELCOME,
        "balcony_view": hotel_info.BALCONY_VIEW,
    }


# ----------------------------------------------------------------------------
# Xonalar
# ----------------------------------------------------------------------------
@app.get("/api/rooms", response_model=List[schemas.RoomOut])
def list_rooms(
    room_type: Optional[str] = None,
    suited_for: Optional[str] = None,
    max_price: Optional[int] = None,
    guests: Optional[int] = None,
    check_in: Optional[date] = None,
    check_out: Optional[date] = None,
    only_available: bool = False,
    db: Session = Depends(get_db),
):
    if check_in and check_out and check_out <= check_in:
        raise HTTPException(400, "Chiqish sanasi kirish sanasidan keyin bo'lishi kerak")
    query = db.query(Room)
    if room_type:
        query = query.filter(Room.room_type == room_type)
    if suited_for:
        query = query.filter(Room.suited_for.contains(suited_for))     # masalan "couple", "family"
    if max_price:
        query = query.filter(Room.price_per_night <= max_price)
    if guests:
        query = query.filter(Room.capacity >= guests)

    rooms = rooms_to_dicts(db, query.order_by(Room.price_per_night).all(), check_in, check_out)
    if only_available and check_in and check_out:
        rooms = [r for r in rooms if r["available"]]
    return rooms


@app.get("/api/rooms/{room_id}", response_model=schemas.RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(404, "Xona topilmadi")
    return room_to_dict(db, room)


@app.get("/api/rooms/{room_id}/reviews", response_model=List[schemas.ReviewOut])
def room_reviews(room_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.room_id == room_id).order_by(Review.created_at.desc()).all()


# ----------------------------------------------------------------------------
# Bronlar
# ----------------------------------------------------------------------------
@app.post("/api/bookings", response_model=schemas.BookingOut)
def create_booking(data: schemas.BookingCreate, db: Session = Depends(get_db)):
    room = db.get(Room, data.room_id)
    if not room:
        raise HTTPException(404, "Xona topilmadi")
    if data.check_in < date.today():
        raise HTTPException(400, "Kirish sanasi o'tib ketgan")
    if data.check_out <= data.check_in:
        raise HTTPException(400, "Chiqish sanasi kirish sanasidan keyin bo'lishi kerak")
    if (data.check_out - data.check_in).days > MAX_NIGHTS:
        raise HTTPException(400, f"Bir bronda eng ko'pi bilan {MAX_NIGHTS} kecha qolish mumkin")
    if data.check_in > date.today() + timedelta(days=MAX_DAYS_AHEAD):
        raise HTTPException(400, "Bronni eng ko'pi bilan 1 yil oldin qilish mumkin")
    if data.guests > room.capacity:
        raise HTTPException(400, f"Bu xonaga {room.capacity} kishigacha sig'adi")
    if not is_room_available(db, room.id, data.check_in, data.check_out):
        raise HTTPException(409, "Bu xona tanlangan sanalarda band")

    booking = Booking(
        room_id=room.id,
        guest_name=data.guest_name,
        guest_email=data.guest_email.lower(),
        guest_phone=data.guest_phone,
        check_in=data.check_in,
        check_out=data.check_out,
        guests=data.guests,
        total_price=calc_total(room, data.check_in, data.check_out),
        doc_type=data.doc_type,
        doc_number=data.doc_number.strip(),
        is_couple=data.is_couple,
        marriage_cert_number=(data.marriage_cert_number or "").strip() or None,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking_to_out(booking)


@app.get("/api/bookings", response_model=List[schemas.BookingOut])
def my_bookings(email: str = Query(...), db: Session = Depends(get_db)):
    rows = (db.query(Booking).options(joinedload(Booking.room))
            .filter(Booking.guest_email == email.lower()).order_by(Booking.created_at.desc()).all())
    return [booking_to_out(b) for b in rows]


@app.post("/api/bookings/{booking_id}/cancel", response_model=schemas.BookingOut)
def cancel_booking(booking_id: int, email: str = Query(...), db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    # Email mos kelmasa ham "topilmadi" deymiz — begona bron mavjudligini bildirmaslik uchun
    if not booking or booking.guest_email != email.lower():
        raise HTTPException(404, "Bron topilmadi")
    if booking.status == "cancelled":
        raise HTTPException(400, "Bron allaqachon bekor qilingan")
    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking_to_out(booking)


# ----------------------------------------------------------------------------
# Sharhlar (AI sentiment bilan)
# ----------------------------------------------------------------------------
@app.post("/api/reviews", response_model=schemas.ReviewOut)
def create_review(data: schemas.ReviewCreate, db: Session = Depends(get_db)):
    if not db.get(Room, data.room_id):
        raise HTTPException(404, "Xona topilmadi")
    label, score = ai.analyze_sentiment(data.comment, data.rating)  # <-- AI shu yerda ishlaydi
    review = Review(**data.model_dump(), sentiment=label, sentiment_score=score)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# ----------------------------------------------------------------------------
# AI
# ----------------------------------------------------------------------------
@app.post("/api/ai/chat")
def ai_chat(data: schemas.ChatRequest, db: Session = Depends(get_db)):
    """Mehmonxona yordamchisi. Xonalar ma'lumotini bazadan olib, AI'ga beradi."""
    rooms = rooms_to_dicts(db, db.query(Room).all())
    messages = [m.model_dump() for m in data.messages]
    answer, source, suggestions = ai.chat_answer(messages, rooms)
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    return {"answer": answer, "source": source, "suggestions": suggestions,
            "images": chatbot.photo_images(last_user, rooms)}         # rasm savoli bo'lsa — suratlar (chatda ko'rsatiladi)


@app.post("/api/ai/recommend")
def ai_recommend(data: schemas.RecommendRequest, db: Session = Depends(get_db)):
    """
    "2 kishi, balkonli, 100$ gacha" kabi erkin matnni tushunib, mos xonalarni topadi.
    Jarayon: matn -> AI filtrlarga ajratadi -> bazadan xonalar -> ball bo'yicha saralash.
    """
    filters = ai.parse_request(data.text)
    rooms = rooms_to_dicts(db, db.query(Room).all(), data.check_in, data.check_out)
    if data.check_in and data.check_out:
        rooms = [r for r in rooms if r["available"]]   # faqat bo'sh xonalar
    return {"filters": filters, "rooms": rank_rooms(rooms, filters)[:4]}


# ----------------------------------------------------------------------------
# Admin panel (X-Admin-Key sarlavhasi kerak)
# ----------------------------------------------------------------------------
@app.get("/api/admin/stats", dependencies=[Depends(require_admin)])
def admin_stats(db: Session = Depends(get_db)):
    today = date.today()
    total_rooms = int(db.query(func.coalesce(func.sum(Room.quantity), 0)).scalar())   # mehmonxonadagi jami xonalar
    confirmed = db.query(Booking).filter(Booking.status == "confirmed")
    occupied_now = confirmed.filter(Booking.check_in <= today, Booking.check_out > today).count()
    revenue = db.query(func.coalesce(func.sum(Booking.total_price), 0)).filter(Booking.status == "confirmed").scalar()

    by_room = (
        db.query(Room.name, func.count(Booking.id))
        .join(Booking, Booking.room_id == Room.id)
        .filter(Booking.status == "confirmed")
        .group_by(Room.name)
        .all()
    )
    sentiments = dict(db.query(Review.sentiment, func.count(Review.id)).group_by(Review.sentiment).all())

    return {
        "total_rooms": total_rooms,
        "occupied_now": occupied_now,
        "occupancy_percent": round(occupied_now / total_rooms * 100) if total_rooms else 0,
        "confirmed_bookings": confirmed.count(),
        "cancelled_bookings": db.query(Booking).filter(Booking.status == "cancelled").count(),
        "revenue": int(revenue),
        "bookings_by_room": [{"room": name, "count": count} for name, count in by_room],
        "sentiments": {
            "positive": sentiments.get("positive", 0),
            "neutral": sentiments.get("neutral", 0),
            "negative": sentiments.get("negative", 0),
        },
    }


@app.get("/api/admin/bookings", response_model=List[schemas.BookingOut], dependencies=[Depends(require_admin)])
def admin_bookings(db: Session = Depends(get_db)):
    rows = db.query(Booking).options(joinedload(Booking.room)).order_by(Booking.created_at.desc()).limit(200).all()
    return [booking_to_out(b) for b in rows]
