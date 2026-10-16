"""
seed.py — baza bo'sh bo'lsa, mehmonxonaning xona turlarini va bir nechta sharhni qo'shadi.
Server ishga tushganda main.py avtomatik chaqiradi.

Xona turlari xalqaro tasnifga mos (kodlar mehmonxona sohasida keng qo'llaniladi):
  SGL — Single (1 kishilik), DBL — Double (er-xotin/juftlik), TWN — Twin (2 ta alohida karavot),
  ACC — Accessible (nogironlar uchun moslashgan), DLX — Deluxe, FAM — Family (oilaviy),
  JSU — Junior Suite, PRS — Presidential Suite.
Qavatlar toifalar bo'yicha AJRATILGAN (oilalar, yakka mehmonlar va h.k. alohida qavatda):
  2-qavat ACC · 3 FAM · 4 SGL · 5–6 DBL · 7 TWN · 8 DLX · 9 JSU+PRS.
Jami: 84 xona (12 + 20 + 16 + 6 + 14 + 8 + 6 + 2).
"""
from sqlalchemy.orm import Session

from models import Review, Room

ROOMS = [
    dict(code="SGL", name="Standart Single", room_type="standard", price_per_night=55, capacity=1, quantity=12,
         size_m2=18, bed_type="1 × yakka karavot (1,20 m)", view="Hovli ko'rinishi", floor=4, floors="4",
         suited_for="solo,business",
         amenities="wifi,tv,konditsioner,ish-stoli,choynak,fen,nonushta",
         description="Yolg'iz sayohatchi yoki xizmat safari uchun ixcham, tinch va arzon xona: keng ish stoli, shaxsiy hammom.",
         image_url="img/room-single.jpg",
         images="img/room-single.jpg|Yotoqxona;img/bath-1.jpg|Dush va hammom;img/corridor-1.jpg|Qavat yo'lagi"),
    dict(code="DBL", name="Standart Double", room_type="standard", price_per_night=70, capacity=2, quantity=20,
         size_m2=22, bed_type="1 × ikki kishilik (1,60 m)", view="Hovli ko'rinishi", floor=5, floors="5–6",
         suited_for="couple,solo,business",
         amenities="wifi,tv,konditsioner,ish-stoli,choynak,fen,sejf,nonushta",
         description="Er-xotin va juftliklar uchun asosiy xona: katta ikki kishilik karavot, ish stoli va seyf.",
         image_url="img/room-double.jpg",
         images="img/room-double.jpg|Yotoqxona;img/bath-4.jpg|Dush va hammom;img/corridor-2.jpg|Qavat yo'lagi"),
    dict(code="TWN", name="Standart Twin", room_type="standard", price_per_night=72, capacity=2, quantity=16,
         size_m2=22, bed_type="2 × yakka karavot (0,90 m)", view="Hovli ko'rinishi", floor=7, floors="7",
         suited_for="friends,business",
         amenities="wifi,tv,konditsioner,ish-stoli,choynak,fen,sejf,nonushta",
         description="Do'stlar yoki hamkasblar uchun ikkita alohida karavotli xona.",
         image_url="img/room-twin.jpg",
         images="img/room-twin.jpg|Yotoqxona (2 karavot);img/bath-2.jpg|Dush va hammom;img/corridor-1.jpg|Qavat yo'lagi"),
    dict(code="ACC", name="Moslashgan xona (Accessible)", room_type="standard", price_per_night=70, capacity=2, quantity=6,
         size_m2=26, bed_type="1 × ikki kishilik (1,60 m), past balandlikda", view="Hovli ko'rinishi", floor=2, floors="2",
         suited_for="accessible,couple",
         amenities="wifi,tv,konditsioner,moslashgan-hammom,choynak,fen,sejf,nonushta",
         description="Nogironligi bo'lgan mehmonlar uchun: eshik kengligi 90 sm dan ortiq, aravachada kirish mumkin bo'lgan dush, tutqichlar, liftga yaqin.",
         image_url="img/bed-acc.jpg",
         images="img/bed-acc.jpg|Yotoqxona;img/bath-2.jpg|Moslashgan hammom;img/corridor-3.jpg|Keng yo'lak"),
    dict(code="DLX", name="Deluxe Double — balkonli", room_type="deluxe", price_per_night=95, capacity=3, quantity=14,
         size_m2=28, bed_type="1 × king-size (1,80 m)", view="Shahar ko'rinishi", floor=8, floors="8",
         suited_for="couple,business",
         amenities="wifi,tv,konditsioner,balkon,minibar,ish-stoli,choynak,kofe-mashina,xalat,fen,sejf,manzara,nonushta",
         description="Keng xona, shahar ko'rinishidagi shaxsiy balkon, king-size karavot va minibar. Uchinchi mehmon uchun qo'shimcha karavot qo'yiladi.",
         image_url="img/bed-double.jpg",
         images="img/bed-double.jpg|Yotoqxona (king-size);img/room-deluxe.jpg|Balkon eshigi va oyna;img/balcony.jpg|Shaxsiy balkon;img/bath-5.jpg|Dush va hammom;img/balcony-view.jpg|Balkondan ko'rinish"),
    dict(code="FAM", name="Family xona", room_type="family", price_per_night=130, capacity=4, quantity=8,
         size_m2=36, bed_type="1 × ikki kishilik (1,60 m) + 2 × yakka (0,90 m)", view="Shahar ko'rinishi", floor=3, floors="3",
         suited_for="family,friends",
         amenities="wifi,tv,konditsioner,balkon,minibar,sejf,choynak,fen,bolalar-beshigi,nonushta",
         description="4 kishigacha oila uchun keng xona: bolalar beshigi bepul, balkon, yetarlicha joy. Bir-biriga ulanadigan xona so'rov bo'yicha.",
         image_url="img/room-family.jpg",
         images="img/room-family.jpg|Yotoqxona;img/bed-family.jpg|Mehmon zonasi;img/bath-3.jpg|Hammom;img/balcony.jpg|Balkon"),
    dict(code="JSU", name="Junior Suite", room_type="suite", price_per_night=150, capacity=3, quantity=6,
         size_m2=42, bed_type="1 × king-size (1,80 m) + divan-karavot", view="Shahar ko'rinishi", floor=9, floors="9",
         suited_for="couple,business,family",
         amenities="wifi,tv,konditsioner,balkon,minibar,sejf,choynak,kofe-mashina,xalat,fen,divan-karavot,ish-stoli,manzara,nonushta",
         description="Yotoq va mehmonxona zonasi bitta xonada: divan-karavot, ish stoli, balkon. Yubiley, asal oyi va uzoq safarlar uchun.",
         image_url="img/room-junior.jpg",
         images="img/room-junior.jpg|Yotoqxona;img/suite-2.jpg|Mehmonxona zonasi;img/bath-5.jpg|Dush va hammom;img/balcony-view.jpg|Balkondan ko'rinish"),
    dict(code="PRS", name="Prezident Suite", room_type="suite", price_per_night=320, capacity=4, quantity=2,
         size_m2=95, bed_type="2 yotoqxona: 2 × king-size (1,80 m)", view="Panorama ko'rinish", floor=9, floors="9",
         suited_for="vip,business,family",
         amenities="wifi,tv,konditsioner,balkon,jakuzi,minibar,sejf,choynak,kofe-mashina,xalat,fen,divan-karavot,ish-stoli,manzara,nonushta",
         description="Eng yuqori qavatdagi 2 yotoqxonali suite: alohida mehmonxona va ovqatlanish zonasi, jakuzi, panoramali manzara.",
         image_url="img/room-presidential.jpg",
         images="img/room-presidential.jpg|Yotoqxona;img/suite-1.jpg|Ikkinchi yotoqxona;img/suite-3.jpg|Mehmonxona zonasi;img/bath-4.jpg|Hammom va jakuzi;img/balcony-view.jpg|Panoramali manzara"),
]

# (xona kodi, muallif, baho, sharh)
REVIEWS = [
    ("DLX", "Aziza", 5, "Juda toza va qulay xona, balkondan manzara ajoyib edi. Tavsiya qilaman!"),
    ("FAM", "Bobur", 4, "Bolalar bilan bordik, xona keng, nonushta yaxshi. Faqat lift sekin ishlaydi."),
    ("SGL", "Dilshod", 3, "Narxiga yarasha oddiy xona. Wi-Fi tez ishladi."),
    ("PRS", "Madina", 5, "Jakuzi va manzara zo'r! Xizmat darajasi a'lo."),
    ("DBL", "Jasur", 5, "Turmush o'rtog'im bilan bordik. Xodimlar xushmuomala, joylashish tez bo'ldi, hammasi toza."),
    ("ACC", "Sevara", 4, "Aravachada yurishimiz uchun eshiklar va hammom qulay edi. Rahmat!"),
]


def seed_if_empty(db: Session) -> None:
    if db.query(Room).count() > 0:
        return
    for data in ROOMS:
        db.add(Room(**data))
    db.commit()

    # Sharhlarga sentiment AI orqali (yoki zaxira usul bilan) qo'yiladi
    from ai import analyze_sentiment

    ids = {r.code: r.id for r in db.query(Room).all()}
    for code, author, rating, comment in REVIEWS:
        label, score = analyze_sentiment(comment, rating)
        db.add(Review(room_id=ids[code], author=author, rating=rating, comment=comment,
                      sentiment=label, sentiment_score=score))
    db.commit()
