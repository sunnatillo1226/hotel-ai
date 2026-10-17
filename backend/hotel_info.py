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
    {"floor": "3", "what": "Oilaviy qavat: faqat oilaviy xonalar (bolalar bilan oilalar uchun, tinch, bolalar o'yin burchagi)"},
    {"floor": "4", "what": "Yakka mehmonlar va xizmat safari: Standart yakka xonalar"},
    {"floor": "5–6", "what": "Juftliklar: Standart ikki kishilik xonalar"},
    {"floor": "7", "what": "Do'stlar va hamkasblar: Twin xonalar"},
    {"floor": "8", "what": "Balkonli Deluxe xonalar (shahar ko'rinishi)"},
    {"floor": "9", "what": "Suite qavati: Kichik lyuks (Junior Suite) va Prezident lyuksi (panoramali manzara)"},
]

# Har bir qavat (bino rasmida bosiladi). Xona turlari bazadagi `floors` maydonidan avtomatik qo'shiladi (main.py).
FLOORS = [
    {"floor": 9, "title": "Suite qavati (VIP)", "what": "Kichik lyuks (Junior Suite) va Prezident lyuksi — eng yuqori qavat, panoramali manzara, alohida lift kaliti"},
    {"floor": 8, "title": "Deluxe qavati", "what": "Faqat balkonli Deluxe xonalar (shahar ko'rinishi)"},
    {"floor": 7, "title": "Twin qavati", "what": "Faqat Twin xonalar — do'stlar va hamkasblar uchun (2 ta alohida karavot)"},
    {"floor": 6, "title": "Juftliklar qavati (2)", "what": "Faqat Standart ikki kishilik xonalar"},
    {"floor": 5, "title": "Juftliklar qavati (1)", "what": "Faqat Standart ikki kishilik xonalar"},
    {"floor": 4, "title": "Yakka mehmonlar qavati", "what": "Faqat Standart yakka xonalar — tinch, xizmat safari uchun qulay"},
    {"floor": 3, "title": "Oilaviy qavat", "what": "Faqat oilaviy xonalar — bolalar bilan oilalar alohida qavatda, tinch; bolalar o'yin burchagi"},
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
    "image": "img/balkon/balkondan-korinish.jpg",
    "direction": f"{_compass(HOTEL['balcony_bearing'])} ({HOTEL['balcony_bearing']}°)",
    "left": f"Toshkent teleminorasi ({_tower['km']:.1f} km, yo'nalishdan {_td}° {_ts}ga)" if _ts == "chap" else "",
    "right": f"Amir Temur xiyoboni va yashil xiyobon ({_park['km']:.1f} km, yo'nalishdan {_pd}° {_ps}ga)",
    "sides_ok": _ts == "chap" and _ps == "o'ng",
    "note": "Surat — namunaviy: boshqa mehmonxona balkonidan olingan shahar ko'rinishi (mehmonxona o'quv loyihasi). Teleminora va xiyobon yo'nalishi yuqoridagi matnda koordinatalardan hisoblangan.",
}

# Mehmonxona suratlari galereyasi (bo'lim bo'yicha). src — frontend/img/ ichida.
GALLERY = [
    {"group": "Bino va kirish", "src": "img/bino/asosiy-surat.jpg", "caption": "Mehmonxona binosi va bog'li hovli"},
    {"group": "Bino va kirish", "src": "img/bino/kechki-korinish.jpg", "caption": "Kechqurungi yoritilgan bino"},
    {"group": "Bino va kirish", "src": "img/bino/bosh-fasad.jpg", "caption": "Bosh fasad"},
    {"group": "Lobby", "src": "img/lobbi/lobbi-resepshn.jpg", "caption": "Lobby va resepshn"},
    {"group": "Lobby", "src": "img/lobbi/lobbi-shisha-tom.jpg", "caption": "Lobby — shisha tomli yorug' zal"},
    {"group": "Lobby", "src": "img/lobbi/lobbi-zinapoya.jpg", "caption": "Lobby — keng zinapoya va marmar pol"},
    {"group": "Lobby", "src": "img/lobbi/lobbi-yoy.jpg", "caption": "Lobby — yoylar va qulay kutish zonasi"},
    {"group": "Lobby", "src": "img/lobbi/lobbi-kutish-zonasi.jpg", "caption": "Lobby — kutish zonasi"},
    {"group": "Lobby", "src": "img/lobbi/resepshn-yogoch.jpg", "caption": "Resepshn (qabul stoli)"},
    {"group": "Lobby", "src": "img/lobbi/lobbi-zamonaviy.jpg", "caption": "Lobby — zamonaviy interyer"},
    {"group": "Yo'laklar", "src": "img/yolak/yolak-1.jpg", "caption": "Qavat yo'lagi"},
    {"group": "Yo'laklar", "src": "img/yolak/yolak-2.jpg", "caption": "Xonalar oldidagi koridor"},
    {"group": "Yo'laklar", "src": "img/yolak/yolak-3.jpg", "caption": "Keng koridor (aravachada yurish mumkin)"},
    {"group": "Restoran va oshxona", "src": "img/restoran/restoran-zali.jpg", "caption": "Restoran zali"},
    {"group": "Restoran va oshxona", "src": "img/restoran/bufet-zali.jpg", "caption": "Bufet zali — shved stoli"},
    {"group": "Restoran va oshxona", "src": "img/restoran/bufet-qandil.jpg", "caption": "Qandilli zal va tabiiy mevalar"},
    {"group": "Restoran va oshxona", "src": "img/restoran/meva-taomlar.jpg", "caption": "Meva va issiq taomlar bufeti"},
    {"group": "Restoran va oshxona", "src": "img/restoran/nonushta-shved-stoli.jpg", "caption": "Shved stoli nonushta"},
    {"group": "Restoran va oshxona", "src": "img/restoran/nonushta-non-shirinlik.jpg", "caption": "Nonushta stoli — non va shirinliklar"},
    {"group": "Restoran va oshxona", "src": "img/restoran/issiq-taomlar-bufeti.jpg", "caption": "Issiq taomlar bufeti"},
    {"group": "Restoran va oshxona", "src": "img/restoran/oshxona-oshpazlar.jpg", "caption": "Oshxona — oshpazlar"},
    {"group": "Restoran va oshxona", "src": "img/restoran/oshxona-professional.jpg", "caption": "Professional oshxona"},
    {"group": "Zallar", "src": "img/zallar/konferensiya-zali.jpg", "caption": "Konferensiya zali"},
    {"group": "Zallar", "src": "img/zallar/banket-zali.jpg", "caption": "Banket / tadbirlar zali"},
    {"group": "Yashil hudud", "src": "img/hovli/favvorali-hovli.jpg", "caption": "Favvorali hovli"},
    {"group": "Yashil hudud", "src": "img/hovli/yashil-atrium.jpg", "caption": "Yashil atrium"},
    {"group": "Yashil hudud", "src": "img/hovli/ichki-hovli.jpg", "caption": "Ichki hovli va piyodalar yo'lagi"},
    {"group": "Yashil hudud", "src": "img/hovli/daraxtli-maydon.jpg", "caption": "Daraxtli dam olish maydonchasi"},
    {"group": "Yashil hudud", "src": "img/hovli/spa-zonasi.jpg", "caption": "Spa va dam olish zonasi"},
    {"group": "Atrofdagi xiyobon", "src": "img/xiyobon/xiyobon-yolagi.jpg", "caption": "Xiyobon yo'lagi"},
    {"group": "Atrofdagi xiyobon", "src": "img/xiyobon/shahar-bogi.jpg", "caption": "Shahar bog'i"},
    {"group": "Atrofdagi xiyobon", "src": "img/xiyobon/xiyobon-yuqoridan.jpg", "caption": "Xiyobon va favvora — yuqoridan"},
    {"group": "Avtoturargoh", "src": "img/avtoturargoh/yopiq-avtoturargoh.jpg", "caption": "Yopiq avtoturargoh"},
]

# Kutib olish xizmati: mehmon kelganda nima bo'ladi (bosqichma-bosqich, rasmlar bilan)
WELCOME = {
    "title": "Kutib olish xizmati",
    "intro": "Mehmonxonaga kirganingizda sizni formadagi xodimlar kutib oladi: eshik oldida, lobbida va resepshnda.",
    "steps": [
        {"n": 1, "title": "Eshik oldida kutib olish", "image": "img/kutib-olish/1-eshik-oldida.jpg",
         "text": "Doorman mashina eshigini ochadi, salomlashadi va sizni kirish eshigigacha kuzatib boradi."},
        {"n": 2, "title": "Lobbida salomlashish", "image": "img/kutib-olish/2-lobbida.jpg",
         "text": "Formadagi xodim lobbida sizni kutib oladi, ismingiz bilan murojaat qiladi, mehmonga choy yoki suv taklif qilinadi."},
        {"n": 3, "title": "Yuk va valet", "image": "img/kutib-olish/3-yuk-va-valet.jpg",
         "text": "Bellboy sumkalaringizni yuk aravachasiga oladi (kvitansiya beriladi). Mashina bo'lsa, valet uni avtoturargohga olib boradi."},
        {"n": 4, "title": "Resepshnda ro'yxatdan o'tish", "image": "img/kutib-olish/4-resepshn.jpg",
         "text": "Administrator bron raqami va shaxsni tasdiqlovchi hujjatni (pasport/ID) tekshiradi, kalit-kartani beradi. Er-xotinlardan nikoh guvohnomasi so'raladi."},
        {"n": 5, "title": "Xonagacha kuzatish", "image": "img/kutib-olish/5-xonagacha.jpg",
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
# "file" — frontend/img/ ichidagi yo'l (mavzu bo'yicha papkalar: bino, lobbi, xonalar, ...).
PHOTO_CREDITS = [
    {"file": "avtoturargoh/yopiq-avtoturargoh.jpg", "author": "Boys in Bristol Photography", "url": "https://www.pexels.com/photo/photo-of-cars-staying-on-under-roof-parking-11873084/"},
    {"file": "balkon/balkon.jpg", "author": "IslandHopper X", "url": "https://www.pexels.com/photo/15210485/"},
    {"file": "bino/asosiy-surat.jpg", "author": "Pavel Danilyuk", "url": "https://www.pexels.com/photo/9119622/"},
    {"file": "bino/bosh-fasad.jpg", "author": "Thắng-Nhật Trần", "url": "https://www.pexels.com/photo/resort-hotel-building-exterior-17619969/"},
    {"file": "bino/kechki-korinish.jpg", "author": "Ayşegül Aytören", "url": "https://www.pexels.com/photo/16099258/"},
    {"file": "hammom/hammom-1.jpg", "author": "Lisa Anna", "url": "https://www.pexels.com/photo/19846350/"},
    {"file": "hammom/hammom-2.jpg", "author": "Max Vakhtbovych", "url": "https://www.pexels.com/photo/7005268/"},
    {"file": "hammom/hammom-3.jpg", "author": "Max Vakhtbovych", "url": "https://www.pexels.com/photo/7031878/"},
    {"file": "hammom/hammom-4.jpg", "author": "Hongyue Stone-Jon Lee", "url": "https://www.pexels.com/photo/16113325/"},
    {"file": "hammom/hammom-5.jpg", "author": "Rana Matloob Hussain", "url": "https://www.pexels.com/photo/26886815/"},
    {"file": "hovli/daraxtli-maydon.jpg", "author": "Dmitry Alexandrovich", "url": "https://www.pexels.com/photo/29024993/"},
    {"file": "hovli/favvorali-hovli.jpg", "author": "Lara", "url": "https://www.pexels.com/photo/28905417/"},
    {"file": "hovli/ichki-hovli.jpg", "author": "SHOX ART", "url": "https://www.pexels.com/photo/31656168/"},
    {"file": "hovli/spa-zonasi.jpg", "author": "Max Vakhtbovych", "url": "https://www.pexels.com/photo/7031704/"},
    {"file": "hovli/yashil-atrium.jpg", "author": "z yan", "url": "https://www.pexels.com/photo/11909503/"},
    {"file": "kutib-olish/1-eshik-oldida.jpg", "author": "cottonbro studio", "url": "https://www.pexels.com/photo/6474530/"},
    {"file": "kutib-olish/2-lobbida.jpg", "author": "cottonbro studio", "url": "https://www.pexels.com/photo/6474521/"},
    {"file": "kutib-olish/3-yuk-va-valet.jpg", "author": "cottonbro studio", "url": "https://www.pexels.com/photo/6474535/"},
    {"file": "kutib-olish/4-resepshn.jpg", "author": "Andrea Piacquadio", "url": "https://www.pexels.com/photo/3771087/"},
    {"file": "kutib-olish/5-xonagacha.jpg", "author": "Andrea Piacquadio", "url": "https://www.pexels.com/photo/3770110/"},
    {"file": "lobbi/lobbi-shisha-tom.jpg", "author": "K", "url": "https://www.pexels.com/photo/2869215/"},
    {"file": "lobbi/lobbi-yoy.jpg", "author": "Iván Rivero", "url": "https://www.pexels.com/photo/1001965/"},
    {"file": "lobbi/lobbi-zamonaviy.jpg", "author": "Chen Te", "url": "https://www.pexels.com/photo/17264519/"},
    {"file": "lobbi/lobbi-zinapoya.jpg", "author": "Quang Nguyen Vinh", "url": "https://www.pexels.com/photo/14011664/"},
    {"file": "lobbi/resepshn-yogoch.jpg", "author": "Quang Nguyen Vinh", "url": "https://www.pexels.com/photo/6876590/"},
    {"file": "restoran/bufet-qandil.jpg", "author": "Magda Ehlers", "url": "https://www.pexels.com/photo/12255469/"},
    {"file": "restoran/bufet-zali.jpg", "author": "Hongyue Stone-Jon Lee", "url": "https://www.pexels.com/photo/16199068/"},
    {"file": "restoran/issiq-taomlar-bufeti.jpg", "author": "Uuganbayar Otgonbayar", "url": "https://www.pexels.com/photo/15467197/"},
    {"file": "restoran/meva-taomlar.jpg", "author": "Western Skyline Hotel", "url": "https://www.pexels.com/photo/4873365/"},
    {"file": "restoran/nonushta-non-shirinlik.jpg", "author": "Matheus Bertelli", "url": "https://www.pexels.com/photo/13871284/"},
    {"file": "restoran/nonushta-shved-stoli.jpg", "author": "Maria Orlova", "url": "https://www.pexels.com/photo/food-on-table-prepare-for-hotel-breakfast-4916557/"},
    {"file": "restoran/oshxona-oshpazlar.jpg", "author": "Rene Terp", "url": "https://www.pexels.com/photo/2544829/"},
    {"file": "restoran/oshxona-professional.jpg", "author": "Emil Lazarian", "url": "https://www.pexels.com/photo/5251019/"},
    {"file": "restoran/restoran-zali.jpg", "author": "Pixabay", "url": "https://www.pexels.com/photo/262047/"},
    {"file": "xiyobon/shahar-bogi.jpg", "author": "Boys in Bristol Photography", "url": "https://www.pexels.com/photo/15583253/"},
    {"file": "xiyobon/xiyobon-yolagi.jpg", "author": "Cherylanne Hsieh", "url": "https://www.pexels.com/photo/10776332/"},
    {"file": "xiyobon/xiyobon-yuqoridan.jpg", "author": "Andrew Mai", "url": "https://www.pexels.com/photo/28946519/"},
    {"file": "xonalar/deluxe-king-karavot.jpg", "author": "Amelia Hallsworth", "url": "https://www.pexels.com/photo/5461582/"},
    {"file": "xonalar/deluxe-xona.jpg", "author": "Pixabay", "url": "https://www.pexels.com/photo/237371/"},
    {"file": "xonalar/ikki-karavotli-xona.jpg", "author": "Zak Chapman", "url": "https://www.pexels.com/photo/two-single-beds-in-well-lit-room-2029722/"},
    {"file": "xonalar/ikki-kishilik-xona.jpg", "author": "Matheus Bertelli", "url": "https://www.pexels.com/photo/13871310/"},
    {"file": "xonalar/kichik-lyuks-dam-olish.jpg", "author": "Stiven Rivera", "url": "https://www.pexels.com/photo/18801080/"},
    {"file": "xonalar/kichik-lyuks-mehmonxona.jpg", "author": "Stiven Rivera", "url": "https://www.pexels.com/photo/18801079/"},
    {"file": "xonalar/kichik-lyuks.jpg", "author": "Moussa Idrissi", "url": "https://www.pexels.com/photo/luxury-hotel-room-with-modern-interior-design-34672504/"},
    {"file": "xonalar/moslashgan-xona.jpg", "author": "Nguyễn Thị Minh Nghi", "url": "https://www.pexels.com/photo/9877452/"},
    {"file": "xonalar/oilaviy-bolalar-karavoti.jpg", "author": "Ahmet ÇÖTÜR", "url": "https://www.pexels.com/photo/two-beds-in-a-room-with-white-walls-28054887/"},
    {"file": "xonalar/oilaviy-mehmon-zonasi.jpg", "author": "Mariette de Villiers", "url": "https://www.pexels.com/photo/5793547/"},
    {"file": "xonalar/oilaviy-xona.jpg", "author": "Quang Nguyen Vinh", "url": "https://www.pexels.com/photo/14021931/"},
    {"file": "xonalar/prezident-ikkinchi-yotoqxona.jpg", "author": "edithub pro", "url": "https://www.pexels.com/photo/18285946/"},
    {"file": "xonalar/prezident-lyuksi.jpg", "author": "Faisal Nisar", "url": "https://www.pexels.com/photo/luxury-bedroom-interior-with-modern-decor-33837741/"},
    {"file": "xonalar/prezident-mehmonxona.jpg", "author": "Anthony Rahayel", "url": "https://www.pexels.com/photo/19689230/"},
    {"file": "xonalar/yakka-xona.jpg", "author": "Pixabay", "url": "https://www.pexels.com/photo/271618/"},
    {"file": "yolak/yolak-1.jpg", "author": "Pixabay", "url": "https://www.pexels.com/photo/277572/"},
    {"file": "yolak/yolak-2.jpg", "author": "Fliqa India", "url": "https://www.pexels.com/photo/30263902/"},
    {"file": "yolak/yolak-3.jpg", "author": "Rafael Rodrigues", "url": "https://www.pexels.com/photo/34728173/"},
    {"file": "zallar/banket-zali.jpg", "author": "Matheus Bertelli", "url": "https://www.pexels.com/photo/17057001/"},
    {"file": "zallar/konferensiya-zali.jpg", "author": "Matheus Bertelli", "url": "https://www.pexels.com/photo/17056964/"},
    {"file": "balkon/balkondan-korinish.jpg", "author": "Kimpton Sawyer Hotel balkonidan (Pexels)", "url": "https://www.pexels.com/photo/18559573/"},
    {"file": "lobbi/lobbi-resepshn.jpg, lobbi/lobbi-kutish-zonasi.jpg", "author": "foydalanuvchi taqdim etgan namunalar (manba/litsenziyasi o'quv loyihasi uchun alohida tekshirilishi kerak)", "url": ""},
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
