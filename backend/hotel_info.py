"""
hotel_info.py — mehmonxona haqidagi barcha ma'lumot BIR JOYDA (yagona manba).

Ichida: HOTEL (nomi, yulduz, manzil), ENTRANCE (favvora, valet), STAFF (xodimlar va forma), LAYOUT va FLOORS (bino/qavatlar),
        DISTANCES (joylashuv), FACILITIES (qulayliklar, avtoturargoh), DOCUMENTS (bron uchun hujjatlar),
        POLICIES (shartlar), AUDIENCES (kimlar uchun), PHOTO_CREDITS (rasm mualliflari), hotel_text() (AI uchun matn).

Undan ikki joyda foydalaniladi:
  1) GET /api/hotel   -> sayt "Mehmonxona haqida", "Qulayliklar", "Hujjatlar" bo'limlarini shundan chizadi
  2) ai.py            -> AI chat shu ma'lumotga tayanib javob beradi (o'zidan to'qimaydi)

Eslatma: bu NAMUNAVIY (o'quv) mehmonxona. Manzil, narx va xizmatlar loyiha parametrlari;
ular xalqaro mezonlarga (Hotelstars Union) va O'zbekiston standartiga (O'z DSt 3296:2018) moslab loyihalangan.
Batafsil: docs/05-mehmonxona-standartlari.md
"""
import math


HOTEL = {
    "name": "Silk Road Grand Hotel",
    "stars": 4,
    "tagline": "Toshkent markazidagi zamonaviy 4 yulduzli shahar mehmonxonasi",
    "demo_note": "Namunaviy (o'quv) mehmonxona: manzil, narx va xizmatlar loyiha parametrlari.",
    "address": "Toshkent sh., Mirobod tumani, Amir Temur xiyoboni yaqinida (namunaviy manzil)",
    "latitude": 41.3125,
    "longitude": 69.2770,
    "balcony_bearing": 60,
    "floors_above": 9,
    "floors_below": 2,
    "elevators": 3,
    "languages": ["o'zbek", "rus", "ingliz"],
    "check_in": "14:00",
    "check_out": "12:00",
    "phone": "+998 71 000 00 00",
    "email": "info@silkroad-grand.example",
}

# Kirish qismi (sayt va rasmdagi binoda ko'rinadi)
ENTRANCE = {
    "fountain": "Bosh kirish oldida favvorali yashil maydon (aylana havza, kechqurun yoritiladi)",
    "canopy": "Yomg'ir va quyoshdan himoya qiluvchi soyabonli kirish, avtomatik shisha eshiklar",
    "valet": "Mashinangizni kirish oldida qoldiring: formadagi valet xodimi uni avtoturargohga olib boradi va so'raganingizda 3–5 daqiqada olib keladi",
    "valet_price": "Mehmonlar uchun bepul (choy puli ixtiyoriy)",
}

# Xodimlar va ularning formasi. Mehmonxona brend ranglari: to'q yashil + oltin; har xodimda ismi yozilgan nishon.
STAFF = [
    {"role": "Eshik oldi xizmatchisi (doorman)", "icon": "🎩", "colors": ["#9b1c24", "#ffffff"],
     "uniform": "Qizil (bordo) forma, oltin tugmalar, oq qo'lqop, qora bosh kiyim",
     "does": "Mehmonni kutib oladi, eshik ochadi, taksi chaqiradi, yomg'irda soyabon tutadi"},
    {"role": "Valet haydovchi", "icon": "🚗", "colors": ["#0f3d2e", "#c8963e", "#1d2a25"],
     "uniform": "To'q yashil kurtka, oltin tugmalar, qora shim, kepka, ismi yozilgan nishon",
     "does": "Mashinani avtoturargohga olib boradi va so'ralganda eshik oldiga olib keladi (raqamli kvitansiya beriladi)"},
    {"role": "Resepshn administratori", "icon": "🛎️", "colors": ["#1d2a25", "#c8963e"],
     "uniform": "Qora kostyum, oq ko'ylak, oltin nishon",
     "does": "Ro'yxatdan o'tkazish (check-in/out), hujjatlarni tekshirish, savollarga javob; 24 soat ishlaydi"},
    {"role": "Yuk tashuvchi (bellboy)", "icon": "🧳", "colors": ["#9b1c24", "#ffffff"],
     "uniform": "Qizil (bordo) forma, oq qo'lqop, qora bosh kiyim",
     "does": "Sumkalarni xonagacha olib chiqadi va chiqishda olib tushadi"},
    {"role": "Konsyerj", "icon": "🗝️", "colors": ["#1d2a25", "#c8963e"],
     "uniform": "Qora kostyum, lapelida oltin kalitlar belgisi",
     "does": "Shahar bo'yicha maslahat, taksi, transfer, restoran va ekskursiya band qilish"},
    {"role": "Xavfsizlik xodimi", "icon": "🛡️", "colors": ["#1d2a25", "#ffffff"],
     "uniform": "Qora forma, nishon",
     "does": "Bino va avtoturargoh xavfsizligi, video-kuzatuv; 24 soat"},
    {"role": "Xona xizmati (housekeeping)", "icon": "🧹", "colors": ["#e8dcc0", "#ffffff"],
     "uniform": "Och rangli forma, oq fartuk",
     "does": "Xonalarni har kuni tozalaydi, ko'rpa-to'shakni almashtiradi"},
]

# Bino tuzilishi (qavatlar)
LAYOUT = [
    {"floor": "−2, −1", "what": "Yopiq yer osti avtoturargoh, valet saqlash joyi, elektromobil quvvatlash joylari"},
    {"floor": "1", "what": "Lobby, 24 soatlik resepshn, konsyerj, restoran va lobby-bar, konferensiya zali (80 kishilik), yuk saqlash"},
    {"floor": "2", "what": "Moslashgan xonalar (nogironligi bo'lgan mehmonlar, liftga eng yaqin), fitnes zal va sauna"},
    {"floor": "3", "what": "Oilaviy qavat: faqat Family xonalar (bolalar bilan oilalar uchun, tinch, bolalar o'yin burchagi)"},
    {"floor": "4", "what": "Yakka mehmonlar va xizmat safari: Standart Single xonalar"},
    {"floor": "5–6", "what": "Juftliklar: Standart Double xonalar"},
    {"floor": "7", "what": "Do'stlar va hamkasblar: Twin xonalar"},
    {"floor": "8", "what": "Balkonli Deluxe xonalar (shahar ko'rinishi)"},
    {"floor": "9", "what": "Suite qavati: Junior Suite va Prezident Suite (panoramali manzara)"},
]

# Har bir qavat (bino rasmida bosiladi). Xona turlari bazadagi `floors` maydonidan avtomatik qo'shiladi (main.py).
FLOORS = [
    {"floor": 9, "title": "Suite qavati (VIP)", "what": "Junior Suite va Prezident Suite — eng yuqori qavat, panoramali manzara, alohida lift kaliti"},
    {"floor": 8, "title": "Deluxe qavati", "what": "Faqat balkonli Deluxe xonalar (shahar ko'rinishi)"},
    {"floor": 7, "title": "Twin qavati", "what": "Faqat Twin xonalar — do'stlar va hamkasblar uchun (2 ta alohida karavot)"},
    {"floor": 6, "title": "Juftliklar qavati (2)", "what": "Faqat Standart Double xonalar"},
    {"floor": 5, "title": "Juftliklar qavati (1)", "what": "Faqat Standart Double xonalar"},
    {"floor": 4, "title": "Yakka mehmonlar qavati", "what": "Faqat Standart Single xonalar — tinch, xizmat safari uchun qulay"},
    {"floor": 3, "title": "Oilaviy qavat", "what": "Faqat Family xonalar — bolalar bilan oilalar alohida qavatda, tinch; bolalar o'yin burchagi"},
    {"floor": 2, "title": "Moslashgan xonalar", "what": "Nogironligi bo'lgan mehmonlar uchun xonalar (liftga eng yaqin), fitnes zal va sauna"},
    {"floor": 1, "title": "Lobby va xizmatlar", "what": "Kirish, 24 soatlik resepshn, restoran, lobby-bar, konferensiya zali, yuk saqlash, konsyerj"},
    {"floor": -1, "title": "Avtoturargoh (1-daraja)", "what": "Yopiq avtoturargoh, nogironlar uchun o'rinlar, 5 ta elektromobil quvvatlash joyi"},
    {"floor": -2, "title": "Avtoturargoh (2-daraja)", "what": "Yopiq avtoturargoh, valet saqlash joyi, texnik xonalar"},
]

# --- Joylashuv: masofalar koordinatalardan HISOBLANADI (haversine), qo'lda yozilmaydi ---
# Diqqat: mehmonxona nuqtasi namunaviy (tanlangan). Mo'ljallar koordinatalari ochiq manbalardan (Wikipedia/OSM), ~ aniqlik.
LANDMARKS = [
    {"place": "Toshkent teleminorasi", "lat": 41.3455694, "lon": 69.2846028, "icon": "📡",
     "note": "balandligi 375 m (Wikipedia); 97 m balandlikda kuzatuv maydonchasi"},
    {"place": "Amir Temur xiyoboni va maydoni", "lat": 41.3111, "lon": 69.2797, "icon": "🌳",
     "note": "markaziy xiyobon; mehmonxona xiyobonning g'arbiy tomonida"},
    {"place": "Toshkent xalqaro aeroporti", "lat": 41.2579, "lon": 69.2812, "icon": "✈️",
     "note": "mashinada ~15–20 daqiqa (tirbandlikda ko'proq)"},
]


def _geo(lat1, lon1, lat2, lon2):
    """Ikki nuqta orasidagi masofa (km, to'g'ri chiziq) va yo'nalish (gradus, shimoldan soat mili bo'yicha)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    km = 2 * r * math.asin(math.sqrt(a))
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return km, (math.degrees(math.atan2(y, x)) + 360) % 360


def _fmt_km(km):
    return f"{round(km * 1000 / 10) * 10} m" if km < 1 else f"{km:.1f} km"


def _compass(b):
    return ["shimol", "shimoli-sharq", "sharq", "janubi-sharq", "janub", "janubi-g'arb", "g'arb", "shimoli-g'arb"][round(b / 45) % 8]


DISTANCES = []
for _l in LANDMARKS:
    _km, _b = _geo(HOTEL["latitude"], HOTEL["longitude"], _l["lat"], _l["lon"])
    _val = f"{_fmt_km(_km)} to'g'ri chiziqda, {_compass(_b)} tomonda"
    if _km < 1.5:
        _val += f" (~{max(1, round(_km / 4.8 * 60))} daqiqa piyoda)"
    DISTANCES.append({"place": _l["place"], "value": _val, "icon": _l["icon"], "note": _l["note"],
                      "km": round(_km, 2), "bearing": round(_b)})
DISTANCES.append({"place": "Eng yaqin metro bekati", "value": "~500 m (6–7 daqiqa piyoda)", "icon": "🚇",
                  "note": "taxminiy, aniq bekat o'rnatilganda yangilanadi"})
DISTANCES.append({"place": "Aeroportdan transfer", "value": "oldindan buyurtma bilan, 15$", "icon": "🚐", "note": ""})

# Balkondan ko'rinish: balkon `balcony_bearing` gradus tomonga qaraydi; mo'ljal chap/o'ngda ekanini hisoblaymiz.
def _side(bearing_to):
    diff = (bearing_to - HOTEL["balcony_bearing"] + 540) % 360 - 180      # -180..180, manfiy = chap
    return "chap" if diff < 0 else "o'ng", abs(round(diff))


_tower = next(d for d in DISTANCES if d["place"] == "Toshkent teleminorasi")
_park = next(d for d in DISTANCES if d["place"].startswith("Amir Temur"))
_ts, _td = _side(_tower["bearing"])
_ps, _pd = _side(_park["bearing"])
BALCONY_VIEW = {
    "image": "img/balcony-view.jpg",
    "direction": f"{_compass(HOTEL['balcony_bearing'])} ({HOTEL['balcony_bearing']}°)",
    "left": f"Toshkent teleminorasi ({_tower['km']:.1f} km, yo'nalishdan {_td}° {_ts}ga)" if _ts == "chap" else "",
    "right": f"Amir Temur xiyoboni va yashil xiyobon ({_park['km']:.1f} km, yo'nalishdan {_pd}° {_ps}ga)",
    "sides_ok": _ts == "chap" and _ps == "o'ng",
    "note": "Surat — namunaviy kollaj: haqiqiy teleminora va xiyobon suratlari birlashtirilgan, mehmonxona o'quv loyihasi.",
}

# Mehmonxona suratlari galereyasi (bo'lim bo'yicha). src — frontend/img/ ichida.
GALLERY = [
    {"group": "Bino va kirish", "src": "img/exterior-pool.jpg", "caption": "Bino va hovuzli hovli"},
    {"group": "Bino va kirish", "src": "img/exterior-facade.jpg", "caption": "Bosh fasad"},
    {"group": "Lobby", "src": "img/lobby-atrium.jpg", "caption": "Lobby va resepshn"},
    {"group": "Lobby", "src": "img/lobby-samarkand.jpg", "caption": "Lobby — kutish zonasi"},
    {"group": "Lobby", "src": "img/lobby-2.jpg", "caption": "Lobby — zamonaviy interyer"},
    {"group": "Yo'laklar", "src": "img/corridor-1.jpg", "caption": "Qavat yo'lagi"},
    {"group": "Yo'laklar", "src": "img/corridor-2.jpg", "caption": "Xonalar oldidagi koridor"},
    {"group": "Yo'laklar", "src": "img/corridor-3.jpg", "caption": "Keng koridor (aravachada yurish mumkin)"},
    {"group": "Restoran va oshxona", "src": "img/restaurant-1.jpg", "caption": "Restoran zali"},
    {"group": "Restoran va oshxona", "src": "img/restaurant-2.jpg", "caption": "Restoran — kechki ovqat"},
    {"group": "Restoran va oshxona", "src": "img/breakfast.jpg", "caption": "Shved stoli nonushta"},
    {"group": "Restoran va oshxona", "src": "img/kitchen-1.jpg", "caption": "Oshxona — oshpazlar"},
    {"group": "Restoran va oshxona", "src": "img/kitchen-2.jpg", "caption": "Professional oshxona"},
    {"group": "Zallar", "src": "img/hall-1.jpg", "caption": "Konferensiya zali"},
    {"group": "Zallar", "src": "img/hall-2.jpg", "caption": "Banket / tadbirlar zali"},
    {"group": "Yashil hudud", "src": "img/garden-fountain.jpg", "caption": "Favvorali hovli"},
    {"group": "Yashil hudud", "src": "img/garden-atrium.jpg", "caption": "Yashil atrium va hovuz"},
    {"group": "Yashil hudud", "src": "img/garden-2.jpg", "caption": "Dam olish bog'i"},
    {"group": "Yashil hudud", "src": "img/garden-3.jpg", "caption": "Yashil maydon"},
    {"group": "Yashil hudud", "src": "img/spa.jpg", "caption": "Spa va dam olish zonasi"},
    {"group": "Atrofdagi xiyobon", "src": "img/park-2.jpg", "caption": "Xiyobon yo'lagi"},
    {"group": "Atrofdagi xiyobon", "src": "img/park-3.jpg", "caption": "Shahar bog'i"},
    {"group": "Atrofdagi xiyobon", "src": "img/park-aerial.jpg", "caption": "Xiyobon va favvora — yuqoridan"},
    {"group": "Avtoturargoh", "src": "img/parking.jpg", "caption": "Yopiq avtoturargoh"},
]

# Kutib olish xizmati: mehmon kelganda nima bo'ladi (bosqichma-bosqich, rasmlar bilan)
WELCOME = {
    "title": "Kutib olish xizmati",
    "intro": "Mehmonxonaga kirganingizda sizni formadagi xodimlar kutib oladi: eshik oldida, lobbida va resepshnda.",
    "steps": [
        {"n": 1, "title": "Eshik oldida kutib olish", "image": "img/welcome-bellman-door.jpg",
         "text": "Doorman mashina eshigini ochadi, salomlashadi va sizni kirish eshigigacha kuzatib boradi."},
        {"n": 2, "title": "Lobbida salomlashish", "image": "img/welcome-bellmen.jpg",
         "text": "Formadagi xodim lobbida sizni kutib oladi, ismingiz bilan murojaat qiladi, mehmonga choy yoki suv taklif qilinadi."},
        {"n": 3, "title": "Yuk va valet", "image": "img/welcome-greeting.jpg",
         "text": "Bellboy sumkalaringizni yuk aravachasiga oladi (kvitansiya beriladi). Mashina bo'lsa, valet uni avtoturargohga olib boradi."},
        {"n": 4, "title": "Resepshnda ro'yxatdan o'tish", "image": "img/welcome-reception.jpg",
         "text": "Administrator bron raqami va shaxsni tasdiqlovchi hujjatni (pasport/ID) tekshiradi, kalit-kartani beradi. Er-xotinlardan nikoh guvohnomasi so'raladi."},
        {"n": 5, "title": "Xonagacha kuzatish", "image": "img/welcome-room-service.jpg",
         "text": "Bellboy sizni liftda xonagacha olib chiqadi, xona jihozlarini tushuntiradi."},
    ],
}

# Qulayliklar va xizmatlar (guruhlar bo'yicha)
FACILITIES = [
    {"group": "Kirish va tashqi ko'rinish", "icon": "⛲", "items": [
        "Favvorali yashil maydon (bosh kirish oldida)",
        "Soyabonli kirish, avtomatik shisha eshiklar, eshik oldi xizmatchisi",
        "Valet posti: mashinani kutib olish va avtoturargohga olib borish",
        "Kechqurun yoritilgan bino va kirish yo'li",
    ]},
    {"group": "Qabul va xizmat", "icon": "🛎️", "items": [
        "24 soat ochiq resepshn (xodim har doim jismonan mavjud)",
        "O'zbek, rus va ingliz tillarida xizmat",
        "3 ta lift, yuk va sumkalarni saqlash xizmati",
        "Uyg'otish xizmati, kir yuvish va dazmollash",
        "Qonun bo'yicha bepul xizmatlar: tez yordam chaqirish, dori qutisi, qaynatilgan suv, ip-igna, bir to'plam idish-tovoq",
    ]},
    {"group": "Avtoturargoh", "icon": "🅿️", "items": [
        "Yopiq yer osti avtoturargoh: 60 o'rin, mehmonlar uchun BEPUL",
        "5 ta elektromobil quvvatlash joyi",
        "Nogironligi bo'lgan mehmonlar uchun 4 ta kengaytirilgan o'rin (liftga yaqin)",
        "Valet: formadagi xodim mashinangizni kirish oldidan olib boradi va olib keladi — mehmonlar uchun bepul",
        "Video-kuzatuv va 24 soat qo'riqlash",
        "Avtobus/mikroavtobus tushirish joyi va velosiped saqlash",
        "Avtomobil balandligi 2,1 m gacha",
    ]},
    {"group": "Ovqatlanish", "icon": "🍳", "items": [
        "Nonushta (shved stoli) har kuni 07:00–10:30, narxga kiritilgan",
        "Restoran: o'zbek va yevropa taomlari",
        "Lobby-bar va xonaga ovqat yetkazish (07:00–23:00)",
        "Bolalar menyusi va bolalar stuli",
    ]},
    {"group": "Xonadagi qulayliklar", "icon": "🛏️", "items": [
        "Bepul tezkor Wi-Fi (xonalarda va umumiy joylarda)",
        "Konditsioner, tekis ekranli TV, elektron kalit-karta",
        "Hammomda xalat va shippak (so'rov bo'yicha), fen, kosmetika to'plami",
        "Choynak va choy/kofe to'plami, ish stoli, seyf (ko'p xonalarda)",
    ]},
    {"group": "Biznes va dam olish", "icon": "💼", "items": [
        "Konferensiya zali: 80 kishigacha, proyektor va ovoz tizimi",
        "Fitnes zal (20 m² dan katta, 4 dan ortiq trenajyor) va sauna",
        "Biznes burchak: kompyuter va printer",
    ]},
    {"group": "Oilalar uchun", "icon": "👨‍👩‍👧", "items": [
        "Bolalar beshigi — BEPUL (so'rov bo'yicha)",
        "6 yoshgacha bolalar mavjud karavotda bepul",
        "Qo'shimcha karavot: 15$ / kecha",
        "Oilaviy xonalar (4 kishigacha) va bir-biriga ulanadigan xonalar (so'rov bo'yicha)",
    ]},
    {"group": "Qulaylik va xavfsizlik", "icon": "♿", "items": [
        "6 ta nogironlar uchun moslashgan xona: keng eshik (90 sm+), pandussiz kirish, aravachada kirish mumkin bo'lgan dush, tutqichlar",
        "Barcha qavatlarga lift orqali chiqish mumkin",
        "Yong'in signalizatsiyasi, evakuatsiya rejalari, video-kuzatuv",
    ]},
]

# Bron qilish va joylashish uchun hujjatlar
DOCUMENTS = {
    "note": "Bron qilishda shaxsni tasdiqlovchi hujjat turi va raqami kiritiladi (SHART). Asl hujjat joylashishda (check-in) resepshnda ko'rsatiladi — ular bron ma'lumotiga mos kelishi kerak.",
    "cards": [
        {"title": "Barcha mehmonlar (shaxsni tasdiqlovchi hujjat)", "icon": "🪪", "points": [
            "Bronda: hujjat turi (pasport / ID-karta / xalqaro pasport) va hujjat raqami kiritiladi.",
            "Check-in da: shu hujjatning ASLI ko'rsatiladi, har bir kattalar mehmon uchun.",
            "Yangi namunadagi haydovchilik guvohnomasi ham shaxsni tasdiqlovchi hujjat sifatida qabul qilinishi mumkin.",
        ]},
        {"title": "Chet el fuqarolari", "icon": "🛂", "points": [
            "Xalqaro pasport (kerak bo'lsa viza bilan).",
            "Mehmonxona chet ellik mehmonni elektron tizimda o'zi ro'yxatga oladi; hujjat nusxasi olinadi.",
            "Ro'yxatdan o'tish qoidalari o'zgarib turadi — safardan oldin rasmiy manbada tekshirib oling.",
        ]},
        {"title": "Er-xotin va juftliklar", "icon": "💑", "points": [
            "Er-xotin sifatida bitta xonaga joylashsangiz, NIKOH GUVOHNOMASI ham kerak (mehmonxonaning ichki qoidasi).",
            "Bronda \"Biz er-xotinmiz\" belgilanadi va nikoh guvohnomasi raqami kiritiladi; check-in da guvohnoma asli (yoki elektron ko'rinishi) ko'rsatiladi.",
            "Do'stlar, hamkasblar yoki qarindoshlar nikoh guvohnomasisiz joylashadi (alohida karavotli Twin xona qulay).",
        ]},
        {"title": "Oilalar (bolalar bilan)", "icon": "👨‍👩‍👧‍👦", "points": [
            "Ota-onalar er-xotin bo'lsa — yuqoridagi qoida: shaxsiy hujjat va nikoh guvohnomasi.",
            "Bolalar uchun ro'yxatga olish maqsadida tug'ilganlik guvohnomasi yoki ID-karta/pasport ma'lumoti olinadi (ichki qoida).",
            "18 yoshgacha bo'lgan shaxslar kattalarsiz joylashtirilmaydi (ichki qoida).",
        ]},
    ],
    "source": "Bu — namunaviy mehmonxonaning ICHKI qoidalari. Diqqat: 2023-yilda O'zbekistonda mehmonxonalarga nikoh guvohnomasi va propiska talab qilishni taqiqlash haqida ommaviy xabarlar chiqqan; rasmiy matnni tasdiqlay olmadim. Real mehmonxona ochishda amaldagi qonunni lex.uz saytida albatta tekshiring.",
}

# Shartlar (siyosat)
POLICIES = [
    {"title": "Check-in / check-out", "text": "Joylashish 14:00 dan, chiqish 12:00 gacha. Erta kirish va kech chiqish — mavjudligiga qarab, so'rov bilan."},
    {"title": "Bekor qilish", "text": "Check-in sanasidan 24 soat oldin bepul bekor qilish mumkin. Kelmasangiz, ko'pi bilan 1 kecha narxi undirilishi mumkin."},
    {"title": "Bolalar", "text": "6 yoshgacha bolalar mavjud karavotda bepul. Qo'shimcha karavot 15$/kecha. Bolalar beshigi bepul."},
    {"title": "Uy hayvonlari", "text": "Uy hayvonlari qabul qilinmaydi (yo'lboshlovchi xizmat itlari bundan mustasno)."},
    {"title": "Chekish", "text": "Barcha xonalar chekilmaydigan. Chekish faqat belgilangan joylarda."},
    {"title": "To'lov", "text": "Bank kartasi yoki naqd pul bilan, joylashish paytida. Onlayn to'lov hozircha yo'q."},
]

# "Kimlar uchun qaysi xona?" — sayt filtri va AI shu yerdan foydalanadi
AUDIENCES = [
    {"key": "solo", "title": "Yolg'iz sayohatchi", "icon": "🧳", "hint": "Qisqa safar yoki xizmat safari: ixcham va arzon xona"},
    {"key": "couple", "title": "Er-xotin / juftlik", "icon": "💑", "hint": "Katta karavotli xona, balkonli yoki suite — dam olish va yubileylar uchun"},
    {"key": "friends", "title": "Do'stlar / hamkasblar", "icon": "👥", "hint": "Ikkita alohida karavot"},
    {"key": "family", "title": "Oilalar (bolalar bilan)", "icon": "👨‍👩‍👧", "hint": "4 kishigacha sig'adigan keng xona, bolalar beshigi bepul"},
    {"key": "business", "title": "Biznes sayohat", "icon": "💼", "hint": "Ish stoli, tinch joy, konferensiya zaliga yaqinlik"},
    {"key": "accessible", "title": "Nogironligi bo'lgan mehmonlar", "icon": "♿", "hint": "Moslashgan hammom va keng eshiklar"},
    {"key": "vip", "title": "VIP / yubiley", "icon": "👑", "hint": "Eng keng suite, alohida mehmonxona zonasi"},
]

# Rasm mualliflari (Pexels litsenziyasi: bepul foydalanish). Rasmlar — namunaviy (illyustrativ).
PHOTO_CREDITS = [
    {"file": "exterior-facade.jpg", "author": "Thắng-Nhật Trần", "url": "https://www.pexels.com/photo/resort-hotel-building-exterior-17619969/"},
    {"file": "lobby-1.jpg", "author": "Max Vakhtbovych", "url": "https://www.pexels.com/photo/modern-spacious-lobby-of-luxury-hotel-6758532/"},
    {"file": "breakfast.jpg", "author": "Maria Orlova", "url": "https://www.pexels.com/photo/food-on-table-prepare-for-hotel-breakfast-4916557/"},
    {"file": "parking.jpg", "author": "Boys in Bristol Photography", "url": "https://www.pexels.com/photo/photo-of-cars-staying-on-under-roof-parking-11873084/"},
    {"file": "room-single.jpg", "author": "thiha soe", "url": "https://www.pexels.com/photo/interior-of-a-hotel-room-5883728/"},
    {"file": "room-double.jpg", "author": "Arina Shabalina", "url": "https://www.pexels.com/photo/a-bed-or-beds-in-a-room-at-hotel-27901676/"},
    {"file": "room-twin.jpg", "author": "Zak Chapman", "url": "https://www.pexels.com/photo/two-single-beds-in-well-lit-room-2029722/"},
    {"file": "room-deluxe.jpg", "author": "Диана Дунаева", "url": "https://www.pexels.com/photo/view-of-old-building-from-room-interior-through-balcony-door-9838766/"},
    {"file": "room-family.jpg", "author": "Ahmet ÇÖTÜR", "url": "https://www.pexels.com/photo/two-beds-in-a-room-with-white-walls-28054887/"},
    {"file": "room-junior.jpg", "author": "Moussa Idrissi", "url": "https://www.pexels.com/photo/luxury-hotel-room-with-modern-interior-design-34672504/"},
    {"file": "room-presidential.jpg", "author": "Faisal Nisar", "url": "https://www.pexels.com/photo/luxury-bedroom-interior-with-modern-decor-33837741/"},
    # Quyidagilar — Pexels (bepul litsenziya); muallif nomi sahifada: https://www.pexels.com/photo/<ID>/
    {"file": "welcome-bellmen.jpg", "author": "Pexels #6474521", "url": "https://www.pexels.com/photo/6474521/"},
    {"file": "welcome-bellman-door.jpg", "author": "Pexels #6474530", "url": "https://www.pexels.com/photo/6474530/"},
    {"file": "welcome-greeting.jpg", "author": "Pexels #6474535", "url": "https://www.pexels.com/photo/6474535/"},
    {"file": "welcome-reception.jpg", "author": "Pexels #3771087", "url": "https://www.pexels.com/photo/3771087/"},
    {"file": "welcome-room-service.jpg", "author": "Pexels #3770110", "url": "https://www.pexels.com/photo/3770110/"},
    {"file": "bath-1.jpg", "author": "Pexels #19846350", "url": "https://www.pexels.com/photo/19846350/"},
    {"file": "bath-2.jpg", "author": "Pexels #7005268", "url": "https://www.pexels.com/photo/7005268/"},
    {"file": "bath-3.jpg", "author": "Pexels #7031878", "url": "https://www.pexels.com/photo/7031878/"},
    {"file": "bath-4.jpg", "author": "Pexels #16113325", "url": "https://www.pexels.com/photo/16113325/"},
    {"file": "bath-5.jpg", "author": "Pexels #26886815", "url": "https://www.pexels.com/photo/26886815/"},
    {"file": "corridor-1.jpg", "author": "Pexels #277572", "url": "https://www.pexels.com/photo/277572/"},
    {"file": "corridor-2.jpg", "author": "Pexels #30263902", "url": "https://www.pexels.com/photo/30263902/"},
    {"file": "corridor-3.jpg", "author": "Pexels #34728173", "url": "https://www.pexels.com/photo/34728173/"},
    {"file": "kitchen-1.jpg", "author": "Pexels #2544829", "url": "https://www.pexels.com/photo/2544829/"},
    {"file": "kitchen-2.jpg", "author": "Pexels #5251019", "url": "https://www.pexels.com/photo/5251019/"},
    {"file": "restaurant-1.jpg", "author": "Pexels #13871284", "url": "https://www.pexels.com/photo/13871284/"},
    {"file": "restaurant-2.jpg", "author": "Pexels #15467197", "url": "https://www.pexels.com/photo/15467197/"},
    {"file": "hall-1.jpg", "author": "Pexels #17056964", "url": "https://www.pexels.com/photo/17056964/"},
    {"file": "hall-2.jpg", "author": "Pexels #17057001", "url": "https://www.pexels.com/photo/17057001/"},
    {"file": "garden-fountain.jpg", "author": "Pexels #28905417", "url": "https://www.pexels.com/photo/28905417/"},
    {"file": "garden-atrium.jpg", "author": "Pexels #11909503", "url": "https://www.pexels.com/photo/11909503/"},
    {"file": "garden-2.jpg", "author": "Pexels #31656168", "url": "https://www.pexels.com/photo/31656168/"},
    {"file": "garden-3.jpg", "author": "Pexels #29024993", "url": "https://www.pexels.com/photo/29024993/"},
    {"file": "park-2.jpg", "author": "Pexels #10776332", "url": "https://www.pexels.com/photo/10776332/"},
    {"file": "park-3.jpg", "author": "Pexels #15583253", "url": "https://www.pexels.com/photo/15583253/"},
    {"file": "park-aerial.jpg", "author": "Pexels #28946519", "url": "https://www.pexels.com/photo/28946519/"},
    {"file": "balcony.jpg", "author": "Pexels #15210485", "url": "https://www.pexels.com/photo/15210485/"},
    {"file": "bed-acc.jpg", "author": "Pexels #14580368", "url": "https://www.pexels.com/photo/14580368/"},
    {"file": "bed-double.jpg", "author": "Pexels #5461582", "url": "https://www.pexels.com/photo/5461582/"},
    {"file": "suite-1.jpg", "author": "Pexels #18285946", "url": "https://www.pexels.com/photo/18285946/"},
    {"file": "suite-2.jpg", "author": "Pexels #18801080", "url": "https://www.pexels.com/photo/18801080/"},
    {"file": "suite-3.jpg", "author": "Pexels #19689230", "url": "https://www.pexels.com/photo/19689230/"},
    {"file": "bed-family.jpg", "author": "Pexels #5793547", "url": "https://www.pexels.com/photo/5793547/"},
    {"file": "lobby-2.jpg", "author": "Pexels #17264519", "url": "https://www.pexels.com/photo/17264519/"},
    {"file": "spa.jpg", "author": "Pexels #7031704", "url": "https://www.pexels.com/photo/7031704/"},
    {"file": "balcony-view.jpg", "author": "kollaj: teleminora — xusenru (Pixabay), xiyobon — Pexels #13760786", "url": "https://pixabay.com/"},
    {"file": "lobby-atrium.jpg, lobby-samarkand.jpg, exterior-pool.jpg", "author": "foydalanuvchi taqdim etgan namunalar (manba/litsenziyasi o'quv loyihasi uchun alohida tekshirilishi kerak)", "url": ""},
]


def hotel_text(rooms_total: int) -> str:
    """AI chat uchun matn: yuqoridagi ma'lumotlardan yig'iladi (qo'lda ikki marta yozilmaydi)."""
    h = HOTEL
    lines = [
        f"Mehmonxona: {h['name']}, {h['stars']} yulduzli, {h['floors_above']} qavatli bino (+{h['floors_below']} yer osti qavat), {rooms_total} ta xona.",
        f"Manzil: {h['address']}.",
        f"Check-in {h['check_in']} dan, check-out {h['check_out']} gacha. Tillar: {', '.join(h['languages'])}.",
        "Joylashuv: " + "; ".join(f"{d['place']} — {d['value']}" for d in DISTANCES) + ".",
    ]
    for g in FACILITIES:
        lines.append(f"{g['group']}: " + "; ".join(g["items"]) + ".")
    lines.append(f"Kirish: {ENTRANCE['fountain']}. Valet: {ENTRANCE['valet']}. {ENTRANCE['valet_price']}.")
    lines.append("Xodimlar va forma: " + "; ".join(f"{p['role']} — {p['uniform']}" for p in STAFF) + ".")
    lines.append("Kutib olish xizmati: " + " ".join(f"{x['n']}) {x['title']} — {x['text']}" for x in WELCOME["steps"]))
    lines.append(f"Balkondan ko'rinish: balkon {BALCONY_VIEW['direction']} tomonga qaraydi; chapda {BALCONY_VIEW['left']}, o'ngda {BALCONY_VIEW['right']}.")
    lines.append("Qavatlar: " + "; ".join(f"{f['floor']}-qavat — {f['what']}" for f in FLOORS) + ".")
    lines.append("Hujjatlar: " + " ".join(f"[{c['title']}] " + " ".join(c["points"]) for c in DOCUMENTS["cards"]))
    lines.append("Shartlar: " + " ".join(f"{p['title']}: {p['text']}" for p in POLICIES))
    groups = {}
    for g in GALLERY:
        groups.setdefault(g["group"], []).append(g["caption"])
    lines.append("SURATLAR (galereya): " + "; ".join(f"{k}: " + ", ".join(v) for k, v in groups.items())
                 + ". Har bir xona turining ham o'z suratlari bor (yotoqxona, hammom, balkon).")
    return "\n".join(lines)
