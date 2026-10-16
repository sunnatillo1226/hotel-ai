"""
services.py — biznes mantiq (qoidalar).

main.py faqat so'rovni qabul qiladi, haqiqiy ishni shu fayldagi funksiyalar bajaradi:
  - xona bandmi yoki yo'qmi tekshirish
  - jami narxni hisoblash
  - AI filtrlariga ko'ra xonalarni baholab saralash
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Booking, Review, Room


def peak_occupancy(db: Session, check_in: date, check_out: date, room_id: Optional[int] = None) -> dict:
    """
    Har bir xona turi uchun: [check_in, check_out) oraliqdagi ENG BAND KECHADA nechta xona band? -> {room_id: son}

    Kesishish qoidasi: eski.check_in < yangi.check_out VA eski.check_out > yangi.check_in.
    Mehmonxonada bir turdagi xona ko'p bo'ladi (quantity), shuning uchun "band/bo'sh" emas, har kechani
    alohida sanaymiz: xona turi faqat biror kechada hamma xonalari band bo'lsa to'ladi.
    Hammasi BITTA so'rov bilan olinadi.
    """
    if check_out <= check_in:        # noto'g'ri sanalar: hisoblash uchun kecha yo'q
        return {}
    query = db.query(Booking.room_id, Booking.check_in, Booking.check_out).filter(
        Booking.status == "confirmed", Booking.check_in < check_out, Booking.check_out > check_in
    )
    if room_id is not None:
        query = query.filter(Booking.room_id == room_id)
    nights = (check_out - check_in).days
    per_night = {}                                   # {room_id: [1-kecha band soni, 2-kecha, ...]}
    for rid, b_in, b_out in query.all():
        counts = per_night.setdefault(rid, [0] * nights)
        for k in range((max(b_in, check_in) - check_in).days, (min(b_out, check_out) - check_in).days):
            counts[k] += 1
    return {rid: max(counts) for rid, counts in per_night.items()}


def is_room_available(db: Session, room_id: int, check_in: date, check_out: date) -> bool:
    """Shu turdan kamida bitta xona shu sanalarda bo'shmi?"""
    room = db.get(Room, room_id)
    if room is None:
        return False
    busiest = peak_occupancy(db, check_in, check_out, room_id).get(room_id, 0)
    return room.quantity - busiest > 0


def calc_total(room: Room, check_in: date, check_out: date) -> int:
    nights = (check_out - check_in).days
    return nights * room.price_per_night


def rating_stats(db: Session) -> dict:
    """
    BARCHA xonalarning o'rtacha reytingi va sharhlar sonini BITTA so'rov bilan oladi.
    Natija: {room_id: (o'rtacha, soni)}.
    (Avval har bir xona uchun alohida so'rov ketardi — bu "N+1 muammosi" va sekin ishlardi.)
    """
    rows = db.query(Review.room_id, func.avg(Review.rating), func.count(Review.id)).group_by(Review.room_id).all()
    return {room_id: (round(float(avg), 1), count) for room_id, avg, count in rows}


def rooms_to_dicts(db: Session, rooms: List[Room], check_in: Optional[date] = None,
                   check_out: Optional[date] = None) -> List[dict]:
    """Ko'p xonani tez aylantirish: jami 2 ta so'rov (reyting + bandlik), xonalar sonidan qat'i nazar."""
    stats = rating_stats(db)
    busy = peak_occupancy(db, check_in, check_out) if check_in and check_out else None
    result = []
    for room in rooms:
        avg, count = stats.get(room.id, (None, 0))
        remaining = None if busy is None else max(0, room.quantity - busy.get(room.id, 0))
        result.append(_room_dict(room, avg, count, None if remaining is None else remaining > 0, remaining))
    return result


def room_to_dict(db: Session, room: Room, available: Optional[bool] = None) -> dict:
    """BITTA xonani aylantiradi (xona sahifasi uchun)."""
    avg, count = (
        db.query(func.avg(Review.rating), func.count(Review.id)).filter(Review.room_id == room.id).one()
    )
    return _room_dict(room, round(float(avg), 1) if avg else None, count, available)


def _split(text: str) -> List[str]:
    return [t.strip() for t in (text or "").split(",") if t.strip()]


def _room_dict(room: Room, avg: Optional[float], count: int, available: Optional[bool],
               remaining: Optional[int] = None) -> dict:
    """Room obyektini API javobiga mos lug'atga aylantiradi."""
    return {
        "id": room.id,
        "code": room.code,
        "name": room.name,
        "room_type": room.room_type,
        "price_per_night": room.price_per_night,
        "capacity": room.capacity,
        "quantity": room.quantity,
        "size_m2": room.size_m2,
        "bed_type": room.bed_type,
        "view": room.view,
        "floor": room.floor,
        "floors": room.floors,
        "suited_for": _split(room.suited_for),
        "amenities": _split(room.amenities),
        "description": room.description,
        "image_url": room.image_url,
        "images": _images(room.images, room.image_url),
        "avg_rating": avg,
        "review_count": count,
        "available": available,
        "remaining": remaining,
    }


def _images(raw: str, fallback: str = "") -> List[dict]:
    """'yo'l|izoh;yo'l|izoh' qatorini [{src, caption}] ro'yxatiga aylantiradi."""
    out = []
    for part in (raw or "").split(";"):
        if part.strip():
            src, _, cap = part.partition("|")
            out.append({"src": src.strip(), "caption": cap.strip()})
    if not out and fallback:
        out.append({"src": fallback, "caption": ""})
    return out


def rank_rooms(rooms: List[dict], filters: dict) -> List[dict]:
    """
    AI ajratgan filtrlarga qarab har bir xonaga ball beradi va eng mosini birinchi qo'yadi.
    Ball tizimi: tur mos +3, "kimlar uchun" mos +3, har bir qulaylik +2, sig'im yetarli +2 (yetmasa xona
    chiqarib tashlanadi), narx limiti ichida +2 (oshsa xona chiqarib tashlanadi), bo'sh bo'lsa +1.
    """
    result = []
    for room in rooms:
        score = 0
        reasons = []

        guests = filters.get("guests")
        if guests:
            if room["capacity"] < guests:
                continue  # sig'maydi — ko'rsatmaymiz
            score += 2
            reasons.append(f"{guests} kishi sig'adi")

        max_price = filters.get("max_price")
        if max_price:
            if room["price_per_night"] > max_price:
                continue
            score += 2
            reasons.append(f"{max_price}$ ichida")

        if filters.get("room_type") and room["room_type"] == filters["room_type"]:
            score += 3
            reasons.append("so'ralgan tur")

        audience = filters.get("audience")
        if audience and audience in room.get("suited_for", []):
            score += 3
            reasons.append("sizga mos")

        for amenity in filters.get("amenities", []):
            if amenity in room["amenities"]:
                score += 2
                reasons.append(amenity)

        if room.get("available") is True:
            score += 1

        result.append({**room, "match_score": score, "match_reasons": reasons})

    result.sort(key=lambda r: (-r["match_score"], r["price_per_night"]))
    return result
