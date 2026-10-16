"""
schemas.py — API orqali kiradigan va chiqadigan ma'lumotlar shakli (Pydantic).
Foydalanuvchi noto'g'ri ma'lumot yuborsa, FastAPI avtomatik xato qaytaradi.
"""
from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class RoomOut(BaseModel):
    id: int
    code: str = ""
    name: str
    room_type: str
    price_per_night: int
    capacity: int
    quantity: int = 1
    size_m2: int = 0
    bed_type: str = ""
    view: str = ""
    floor: int
    floors: str = ""
    suited_for: List[str] = []
    amenities: List[str]
    description: str
    image_url: str
    images: List[dict] = []            # [{src, caption}] — xonaning ko'p suratlari
    avg_rating: Optional[float] = None
    review_count: int = 0
    available: Optional[bool] = None   # sana berilganda to'ldiriladi
    remaining: Optional[int] = None    # sana berilganda: shu sanalarda nechta xona qolgan


DOC_TYPES = ("passport", "id_card", "foreign_passport")     # pasport, ID-karta, xalqaro pasport


class BookingCreate(BaseModel):
    room_id: int
    guest_name: str = Field(min_length=2, max_length=100)
    guest_email: EmailStr
    guest_phone: str = ""
    check_in: date
    check_out: date
    guests: int = Field(default=1, ge=1, le=10)
    # Shaxsni tasdiqlovchi hujjat — har bir bronda SHART (asl hujjat check-in da ko'rsatiladi)
    doc_type: Literal["passport", "id_card", "foreign_passport"]
    doc_number: str = Field(min_length=5, max_length=20, pattern=r"^[A-Za-z0-9 \-]+$")
    # Er-xotin sifatida joylashsa — nikoh guvohnomasi raqami SHART (mehmonxonaning ichki qoidasi)
    is_couple: bool = False
    marriage_cert_number: Optional[str] = Field(default=None, max_length=30)

    @model_validator(mode="after")
    def check_couple(self):
        if self.is_couple:
            if self.guests < 2:
                raise ValueError("Er-xotin bo'lib joylashish uchun kamida 2 mehmon bo'lishi kerak")
            if not self.marriage_cert_number or len(self.marriage_cert_number.strip()) < 3:
                raise ValueError("Er-xotin uchun nikoh guvohnomasi raqamini kiriting")
        return self


class BookingOut(BaseModel):
    id: int
    code: str
    room_id: int
    room_name: str
    guest_name: str
    guest_email: str
    guest_phone: str
    check_in: date
    check_out: date
    guests: int
    total_price: int
    status: str
    created_at: datetime
    doc_type: Optional[str] = None
    doc_number_masked: Optional[str] = None     # to'liq raqam API orqali qaytarilmaydi (maxfiylik): "••••567"
    is_couple: bool = False


class ReviewCreate(BaseModel):
    room_id: int
    author: str = Field(min_length=2, max_length=100)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=3, max_length=1000)


class ReviewOut(BaseModel):
    id: int
    room_id: int
    author: str
    rating: int
    comment: str
    sentiment: str
    sentiment_score: float
    created_at: datetime


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=1000)


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(min_length=1, max_length=40)


class RecommendRequest(BaseModel):
    text: str = Field(min_length=3, max_length=500)
    check_in: Optional[date] = None
    check_out: Optional[date] = None
