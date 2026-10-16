"""
models.py — baza jadvallari (3 ta jadval).

Room    — xonalar
Booking — bronlar (Room bilan bog'langan)
Review  — mehmonlar sharhlari (Room bilan bog'langan, AI sentiment bilan)
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from database import Base


def utcnow():
    """Hozirgi UTC vaqt (Python 3.12+ da datetime.utcnow() eskirgan, shuning uchun shu usul)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), default="")               # xalqaro xona kodi: SGL, DBL, TWN, DLX, FAM, JSU, PRS, ACC
    name = Column(String(100), nullable=False)          # "Standart Double"
    room_type = Column(String(30), nullable=False)      # toifa: standard / deluxe / family / suite
    price_per_night = Column(Integer, nullable=False)   # $ da (oddiylik uchun)
    capacity = Column(Integer, nullable=False)          # nechta mehmon sig'adi
    quantity = Column(Integer, default=1)               # shu turdagi nechta xona bor (mehmonxonada)
    size_m2 = Column(Integer, default=0)                # xona maydoni (m², hammom bilan)
    bed_type = Column(String(120), default="")          # "1 × ikki kishilik (1,60 m)"
    view = Column(String(60), default="")               # ko'rinish: shahar / hovli ...
    floor = Column(Integer, default=1)                  # eng past qavat
    floors = Column(String(20), default="")             # qavatlar oralig'i, masalan "3–5"
    suited_for = Column(String(120), default="")        # kimlar uchun: "couple,business" (vergul bilan)
    amenities = Column(String(300), default="")         # "wifi,tv,balkon" (vergul bilan)
    description = Column(Text, default="")
    images = Column(Text, default="")                   # "yo'l|izoh;yo'l|izoh" — xonaning ko'p suratlari
    image_url = Column(String(500), default="")         # saytdagi rasm yo'li; bo'sh bo'lsa, gradient chiqadi

    bookings = relationship("Booking", back_populates="room")
    reviews = relationship("Review", back_populates="room")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    guest_name = Column(String(100), nullable=False)
    guest_email = Column(String(120), nullable=False)
    guest_phone = Column(String(30), default="")
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    guests = Column(Integer, default=1)
    total_price = Column(Integer, nullable=False)
    status = Column(String(20), default="confirmed")    # confirmed / cancelled
    created_at = Column(DateTime, default=utcnow)
    # Shaxsni tasdiqlovchi hujjat (bron uchun shart) va er-xotin uchun nikoh guvohnomasi raqami
    doc_type = Column(String(20), default="")           # passport / id_card / foreign_passport
    doc_number = Column(String(30), default="")
    is_couple = Column(Boolean, default=False)
    marriage_cert_number = Column(String(30), nullable=True)

    room = relationship("Room", back_populates="bookings")

    # Indekslar — qidiruvni tezlashtiradi (kitobdagi mundarija kabi):
    #  1) xona + sana bo'yicha band-bo'shlikni tekshirish uchun
    #  2) "Mening bronlarim" email bo'yicha qidirish uchun
    __table_args__ = (
        Index("ix_booking_room_dates", "room_id", "check_in", "check_out"),
        Index("ix_booking_email", "guest_email"),
    )


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    author = Column(String(100), nullable=False)
    rating = Column(Integer, nullable=False)            # 1..5
    comment = Column(Text, nullable=False)
    sentiment = Column(String(20), default="neutral")   # AI aniqlaydi: positive / neutral / negative
    sentiment_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utcnow)

    room = relationship("Room", back_populates="reviews")
