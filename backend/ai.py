"""
ai.py — sun'iy intellekt qismi (Hugging Face).

Bu faylda 3 ta AI funksiya bor:
  1. chat_answer()       — mehmonxona yordamchisi (savol-javob chat)
  2. parse_request()     — "2 kishi, balkonli, 80$ gacha" kabi matndan filtrlarni ajratib oladi
  3. analyze_sentiment() — sharh ijobiy/salbiy ekanini aniqlaydi

Hugging Face tokeni (HF_TOKEN) bo'lmasa yoki internet ishlamasa, dastur TO'XTAMAYDI:
oddiy qoidalarga asoslangan zaxira (fallback) javoblar ishlaydi. Shuning uchun sayt doim ishlaydi.
"""
import json
import os
import re
from typing import Dict, List, Optional, Tuple

import requests

import chatbot
import hotel_info

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen3-8B")
HF_URL = "https://router.huggingface.co/v1/chat/completions"

# Mehmonxona ma'lumoti bitta joyda turadi: hotel_info.py (sayt ham, AI ham shundan oladi)



has_word = chatbot.has_word      # bitta joyda yozilgan (chatbot.py), bu yerda ham ishlatiladi


# ---------------------------------------------------------------------------
# Past darajadagi funksiya: Hugging Face'ga so'rov yuborish
# ---------------------------------------------------------------------------
def hf_chat(messages: List[Dict], max_tokens: int = 400, temperature: float = 0.4, timeout: int = 20) -> Optional[str]:
    """
    Hugging Face'dan javob oladi. Xato bo'lsa None qaytaradi (dastur yiqilmaydi).
    timeout — AI javobini kutish chegarasi (soniya). Oshib ketsa, zaxira rejimga o'tiladi,
    shunda mehmon uzoq kutib qolmaydi.
    """
    if not HF_TOKEN:
        return None
    try:
        resp = requests.post(
            HF_URL,
            headers={"Authorization": f"Bearer {HF_TOKEN}"},
            json={
                "model": HF_MODEL,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=(4, timeout),   # (ulanish uchun 4 s, javob uchun `timeout` s)
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"] or ""
        # Ba'zi modellar "o'ylash" qismini <think>...</think> ichida yozadi — uni olib tashlaymiz
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        return text or None
    except (requests.RequestException, KeyError, IndexError, ValueError) as e:  # tarmoq, token, limit, kutilmagan javob
        print(f"[AI] Hugging Face xatosi: {e}")
        return None


def ai_enabled() -> bool:
    return bool(HF_TOKEN)


# ---------------------------------------------------------------------------
# 1) Chat yordamchi
# ---------------------------------------------------------------------------
def rooms_to_text(rooms: list) -> str:
    """Xonalar ro'yxatini AI'ga beriladigan matnga aylantiradi (AI haqiqiy ma'lumot asosida javob beradi)."""
    lines = []
    for r in rooms:
        lines.append(
            f"- {r['name']} ({r['room_type']}): {r['price_per_night']}$ / kecha, "
            f"{r['capacity']} kishigacha, {r.get('size_m2', '?')} m², {r.get('bed_type', '')}, "
            f"jami {r.get('quantity', 1)} ta, kimlar uchun: {', '.join(r.get('suited_for', []))}, "
            f"qulayliklar: {', '.join(r['amenities'])}"
        )
    return "\n".join(lines)


SYSTEM_RULES = """Sen {hotel} mehmonxonasining AI yordamchisisan (mehmonlar bilan yozishmada).

USLUB
- Foydalanuvchi qaysi tilda yozsa (o'zbek, rus, ingliz), SHU tilda javob ber. Iliq, hurmatli, tabiiy gapir ("siz" deb murojaat qil).
- Avval savolga to'g'ridan-to'g'ri javob ber, keyin kerak bo'lsa 1 ta foydali qo'shimcha ayt. Odatda 2–4 gap. Ro'yxatni faqat 3 va undan ko'p band bo'lganda ishlat.
- Salomlashishga qisqa salom bilan javob ber, har xabarda qayta salom berma.
- Savol noaniq bo'lsa (masalan "xona kerak"), 1 ta aniqlashtiruvchi savol ber: nechta mehmon, sana, byudjet.
- Oldingi xabarlardagi kontekstni eslab qol ("narxi qancha?" — oldin gap bo'lgan xona haqida).

QOIDALAR
- FAQAT quyidagi ma'lumotlarga tayan. Narx, vaqt, xizmat va qoidalarni o'zingdan to'qima. Ma'lumot yo'q bo'lsa, ochiq ayt va resepshnga murojaat qilishni tavsiya qil: {phone}.
- Mehmonxonaga aloqasi yo'q savollarga (siyosat, dasturlash, tibbiy maslahat va h.k.) muloyim rad javobi ber va mehmonxona mavzusiga qaytar.
- Bron qilishni sen amalga oshirma: foydalanuvchini saytdagi «Xonalar» bo'limiga va bron formasiga yo'nalt.
- Pasport, karta raqami va boshqa shaxsiy ma'lumotni chatda so'rama; foydalanuvchi yozsa, buni faqat bron formasiga kiritishni ayt.
- Hujjat qoidasi: shaxsni tasdiqlovchi hujjat hamma uchun; er-xotin sifatida joylashganlar uchun nikoh guvohnomasi; do'st/hamkasb/qarindoshlardan guvohnoma so'ralmaydi. Qoidalar o'zgarishi mumkin — aniqlik uchun resepshn.
- Markdown sarlavha va ** belgilarini ishlatma, oddiy matn yoz."""


def build_system_prompt(rooms: list) -> str:
    rooms_total = sum(r.get("quantity", 1) for r in rooms)
    h = hotel_info.HOTEL
    return (SYSTEM_RULES.format(hotel=h["name"], phone=h["phone"])
            + f"\n\nMEHMONXONA HAQIDA:\n{hotel_info.hotel_text(rooms_total)}\n\nXONA TURLARI:\n{rooms_to_text(rooms)}")


def chat_answer(messages: List[Dict], rooms: list) -> Tuple[str, str, List[str]]:
    """
    Chatga javob qaytaradi: (javob, manba, keyingi savol takliflari). Manba: 'ai' yoki 'fallback'.
    Avval Hugging Face AI; u ishlamasa chatbot.py dagi ball tizimi javob beradi.
    """
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    fallback_text, suggestions = chatbot.reply(last_user, messages, rooms)
    # shaxsiy ma'lumot yozilgan bo'lsa AI'ga YUBORMAYMIZ (maxfiylik): ogohlantirish qaytariladi
    if chatbot.contains_personal_data(last_user):
        return fallback_text, "fallback", suggestions
    history = [{"role": m["role"], "content": m["content"]} for m in messages[-8:]]
    answer = hf_chat([{"role": "system", "content": build_system_prompt(rooms)}] + history, max_tokens=350)
    if answer:
        return answer, "ai", suggestions
    return fallback_text, "fallback", suggestions


# ---------------------------------------------------------------------------
# 2) Tabiiy tildagi so'rovdan filtr ajratish
# ---------------------------------------------------------------------------
KNOWN_AMENITIES = ["wifi", "tv", "konditsioner", "balkon", "jakuzi", "minibar", "nonushta", "sejf", "manzara",
                   "choynak", "fen", "xalat", "ish-stoli", "kofe-mashina", "divan-karavot", "bolalar-beshigi",
                   "moslashgan-hammom"]
AMENITY_WORDS = {
    "wifi": ["wifi", "wi-fi", "internet"],
    "tv": ["tv", "televizor"],
    "konditsioner": ["konditsioner", "kondisioner", "sovutgich"],
    "balkon": ["balkon", "terrasa"],
    "jakuzi": ["jakuzi", "jacuzzi", "vanna"],
    "minibar": ["minibar"],
    "nonushta": ["nonushta", "breakfast"],
    "sejf": ["sejf", "seyf", "safe"],
    "manzara": ["manzara", "ko'rinish", "view"],
    "choynak": ["choynak", "choy"],
    "fen": ["fen"],
    "xalat": ["xalat"],
    "ish-stoli": ["ish stoli", "ish-stoli", "stol"],
    "kofe-mashina": ["kofe"],
    "divan-karavot": ["divan"],
    "bolalar-beshigi": ["beshik"],
    "moslashgan-hammom": ["moslashgan", "aravacha", "nogiron"],
}
# Kim uchun? (hotel_info.AUDIENCES kalitlari bilan bir xil)
AUDIENCE_WORDS = {
    "accessible": ["nogiron", "aravacha", "accessible", "moslashgan"],
    "vip": ["vip", "yubiley", "prezident", "president"],
    "family": ["oila", "bola", "family", "farzand"],
    "couple": ["er-xotin", "er xotin", "xotinim", "turmush", "juftlik", "asal oyi", "couple", "honeymoon", "sevgilim"],
    "friends": ["do'st", "dost", "friends", "hamkasb"],
    "business": ["biznes", "xizmat safari", "business", "komandirovka", "ish bilan"],
    "solo": ["yolg'iz", "yolgiz", "o'zim", "solo", "alone"],
}
AUDIENCE_KEYS = list(AUDIENCE_WORDS)
TYPE_WORDS = {
    "family": ["oila", "bola", "family", "farzand"],
    "suite": ["lyuks", "lux", "suite", "premium", "hashamat"],
    "deluxe": ["deluxe", "delyuks"],
    "standard": ["standart", "standard", "oddiy", "arzon"],
}


def parse_request(text: str) -> dict:
    """
    "Oilam bilan 4 kishi, balkonli, 120$ gacha" -> {"guests": 4, "max_price": 120, "amenities": ["balkon"], "room_type": "family"}
    Avval AI'dan so'raymiz, bo'lmasa oddiy regex bilan.
    """
    prompt = (
        "Quyidagi mehmon so'rovidan filtrlarni JSON qilib chiqar. Faqat JSON qaytar, boshqa matn yozma.\n"
        'Format: {"guests": son yoki null, "max_price": son yoki null, '
        '"room_type": "standard"|"deluxe"|"family"|"suite"|null, "amenities": [ro\'yxat], '
        '"audience": "solo"|"couple"|"friends"|"family"|"business"|"accessible"|"vip"|null}\n'
        f"amenities faqat shulardan bo'lsin: {', '.join(KNOWN_AMENITIES)}.\n"
        f"So'rov: {text}"
    )
    raw = hf_chat([{"role": "user", "content": prompt}], max_tokens=200, temperature=0.0, timeout=8)
    if raw:
        try:
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            data = json.loads(match.group(0))
            return {
                "guests": _to_int(data.get("guests")),
                "max_price": _to_int(data.get("max_price")),
                "room_type": data.get("room_type") if data.get("room_type") in TYPE_WORDS else None,
                "amenities": [a for a in (data.get("amenities") or []) if a in KNOWN_AMENITIES],
                "audience": data.get("audience") if data.get("audience") in AUDIENCE_KEYS else None,
                "source": "ai",
            }
        except (ValueError, AttributeError, TypeError) as e:
            print(f"[AI] JSON o'qishda xato: {e}")
    return {**parse_request_fallback(text), "source": "fallback"}


def _to_int(value) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def parse_request_fallback(text: str) -> dict:
    t = text.lower()
    guests = None
    m = re.search(r"(\d+)\s*(kishi|nafar|odam|person|people|guest|mehmon)", t)
    if m:
        guests = int(m.group(1))
    max_price = None
    m = re.search(r"(\d+)\s*(\$|usd|dollar|dol)", t) or re.search(r"(\d+)\s*(gacha|dan arzon)", t)
    if m:
        max_price = int(m.group(1))
    room_type = None
    for rtype, words in TYPE_WORDS.items():
        if has_word(t, words):
            room_type = rtype
            break
    amenities = [a for a, words in AMENITY_WORDS.items() if has_word(t, words)]
    audience = next((k for k, words in AUDIENCE_WORDS.items() if has_word(t, words)), None)
    return {"guests": guests, "max_price": max_price, "room_type": room_type, "amenities": amenities,
            "audience": audience}


# ---------------------------------------------------------------------------
# 3) Sharh sentimenti
# ---------------------------------------------------------------------------
POSITIVE = ["yaxshi", "zo'r", "ajoyib", "toza", "qulay", "tavsiya", "good", "great", "clean", "nice",
            "excellent", "amazing", "perfect", "rahmat", "chiroyli", "yoqdi", "отлично", "хорошо", "чисто"]
NEGATIVE = ["yomon", "iflos", "shovqin", "qimmat", "sekin", "bad", "dirty", "noisy", "terrible", "worst",
            "rude", "broken", "buzilgan", "yoqmadi", "ужасно", "плохо", "грязно"]


def analyze_sentiment(comment: str, rating: int) -> Tuple[str, float]:
    """Qaytaradi: (positive|neutral|negative, ball -1.0 dan +1.0 gacha)."""
    prompt = (
        "Mehmonxona sharhining kayfiyatini aniqla. Faqat bitta so'z qaytar: positive, neutral yoki negative.\n"
        f"Sharh: {comment}"
    )
    raw = hf_chat([{"role": "user", "content": prompt}], max_tokens=10, temperature=0.0, timeout=8)
    if raw:
        word = raw.strip().lower()
        for label, score in (("positive", 0.8), ("negative", -0.8), ("neutral", 0.0)):
            if label in word:
                return label, score
    return _sentiment_fallback(comment, rating)


def _sentiment_fallback(comment: str, rating: int) -> Tuple[str, float]:
    c = comment.lower()
    pos = sum(w in c for w in POSITIVE)
    neg = sum(w in c for w in NEGATIVE)
    score = (pos - neg) * 0.3 + (rating - 3) * 0.2
    score = max(-1.0, min(1.0, score))
    if score > 0.15:
        return "positive", round(score, 2)
    if score < -0.15:
        return "negative", round(score, 2)
    return "neutral", round(score, 2)
