"""
chatbot.py — suhbat mexanizmi (AI ishlamaganda ham yaxshi, tushunarli javob beradi).

Nega kerak? Hugging Face tokeni yo'q yoki internet uzilgan bo'lsa ham mehmon "yordamchi"dan foydali javob olishi kerak.
Bu fayl oddiy "kalit so'z" o'rniga ball tizimi bilan ishlaydi:

  1) Tilni aniqlaydi: o'zbek / rus / ingliz — javobni shu tilda beradi
  2) Savol qaysi mavzuga (intent) mos ekanini BALL bilan tanlaydi (uzunroq so'z mosligi — ko'proq ball)
  3) Xona nomi aytilsa ("Family xona qancha?"), shu xona haqida aniq javob beradi; "narxi qancha?" kabi qisqa
     savollarda oldingi suhbatdagi xonani eslab qoladi
  4) "2 kishi, 100$ gacha" kabi talabda xonalarni tavsiya qiladi (services.rank_rooms)
  5) Har javobdan keyin 2–3 ta "keyingi savol" taklifini qaytaradi (sayt tugma qilib ko'rsatadi)
  6) Shaxsiy ma'lumot (pasport/karta raqami) yozilsa, ogohlantiradi

Barcha ma'lumot hotel_info.py va bazadagi xonalardan olinadi — javoblarda raqamlar qo'lda yozilmagan.
"""
import re
from typing import Dict, List, Optional, Tuple

import hotel_info
from hotel_info import HOTEL

LANGS = ("uz", "ru", "en")


# ---------------------------------------------------------------------------
# Yordamchi funksiyalar
# ---------------------------------------------------------------------------
def normalize(text: str) -> str:
    """Kichik harf, har xil apostroflarni bitta ' ga keltirish (o‘, o’, oʻ -> o')."""
    t = text.lower()
    for ch in ("‘", "’", "ʻ", "ʼ", "`", "´"):
        t = t.replace(ch, "'")
    return t


def has_word(text: str, words: List[str]) -> bool:
    """Kalit so'z SO'Z BOSHIDAN uchrasa True ("gacha" ichidagi "ac" mos kelmaydi)."""
    return any(re.search(r"(?<!\w)" + re.escape(w), text) for w in words)


def detect_lang(text: str) -> str:
    """Matn tilini taxminan aniqlaydi: 'ru' (kirill), 'en' (ingliz so'zlar ko'p) yoki 'uz'."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "uz"
    cyr = sum("Ѐ" <= c <= "ӿ" for c in letters)
    if cyr / len(letters) > 0.4:
        return "ru"
    t = normalize(text)
    en_words = ["the", "is", "are", "do", "does", "you", "what", "how", "where", "when", "can", "have", "has", "hotel",
                "room", "rooms", "price", "cost", "much", "breakfast", "parking", "book", "booking", "need", "want",
                "please", "hello", "hi", "thanks", "thank", "check", "pets", "wifi", "airport", "cancel", "documents"]
    uz_words = ["bormi", "qancha", "qanday", "kerak", "xona", "narx", "nima", "qayerda", "necha", "uchun", "va",
                "bilan", "mi", "emas", "bor", "yo'q", "iltimos", "salom", "rahmat", "menga", "bizga"]
    words = re.findall(r"[a-z']+", t)
    en = sum(w in en_words for w in words)
    uz = sum(w in uz_words for w in words)
    return "en" if en > uz and en >= 1 else "uz"


def L(uz: str, ru: Optional[str] = None, en: Optional[str] = None) -> Dict[str, Optional[str]]:
    return {"uz": uz, "ru": ru, "en": en}


def policy(title_start: str) -> str:
    return next((p["text"] for p in hotel_info.POLICIES if p["title"].startswith(title_start)), "")


def money(n) -> str:
    return f"{n}$"


# ---------------------------------------------------------------------------
# Xonalar: nomlar va tavsif
# ---------------------------------------------------------------------------
ROOM_ALIASES = {
    "SGL": ["single", "singl", "yakka xona", "bir kishilik", "1 kishilik", "сингл", "одноместн"],
    "DBL": ["double", "dabl", "ikki kishilik", "дабл", "двухместн"],
    "TWN": ["twin", "tvin", "ikki karavotli", "2 karavotli", "твин"],
    "ACC": ["accessible", "moslashgan xona", "moslashgan", "аксессибл"],
    "DLX": ["deluxe", "hashamatli", "delyuks", "deluks", "делюкс", "де-люкс"],
    "FAM": ["family xona", "family", "oilaviy xona", "семейн", "фэмили"],
    "JSU": ["junior", "kichik lyuks", "yunior", "джуниор", "полулюкс"],
    "PRS": ["prezident lyuksi", "prezident", "president", "presidential", "президентск"],
}


def find_room(text: str, rooms: list) -> Optional[dict]:
    """Matnda xona nomi bormi? Bo'lsa — o'sha xona (dict)."""
    t = normalize(text)
    for code, words in ROOM_ALIASES.items():
        if has_word(t, words):
            return next((r for r in rooms if r.get("code") == code), None)
    return None


def room_summary(r: dict, lang: str) -> str:
    amen = ", ".join(r["amenities"][:6])
    if lang == "uz":
        return (f"{r['name']} ({r['code']}): {money(r['price_per_night'])}/kecha, {r['size_m2']} m², {r['bed_type']}, "
                f"{r['capacity']} kishigacha, {r['floors']}-qavat, ko'rinishi: {r['view']}. Jami {r['quantity']} ta xona.\n"
                f"Qulayliklar: {amen}. {r['description']}")
    if lang == "ru":
        return (f"{r['name']} ({r['code']}): {money(r['price_per_night'])} за ночь, {r['size_m2']} м², до {r['capacity']} гостей, "
                f"этаж {r['floors']}. Удобства: {amen}. Подробности и фото — в разделе «Номера» на сайте.")
    return (f"{r['name']} ({r['code']}): {money(r['price_per_night'])} per night, {r['size_m2']} m², up to {r['capacity']} guests, "
            f"floor {r['floors']}, {r['bed_type']}. Amenities: {amen}. See photos in the Rooms section.")


def room_attribute(r: dict, q: str, lang: str) -> Optional[str]:
    """Xona haqida aniq savol bo'lsa (narx/hajm/qavat/karavot/sig'im) — faqat shuni qaytaradi."""
    n = r["name"]
    if has_word(q, ["narx", "qancha", "necha pul", "price", "cost", "how much", "цена", "сколько", "стоит"]):
        return {"uz": f"{n} — kechasiga {money(r['price_per_night'])}.",
                "ru": f"{n} — {money(r['price_per_night'])} за ночь.",
                "en": f"{n} costs {money(r['price_per_night'])} per night."}[lang]
    if has_word(q, ["qavat", "etaj", "floor", "этаж"]):
        return {"uz": f"{n} {r['floors']}-qavatda joylashgan.", "ru": f"{n} находится на {r['floors']} этаже.",
                "en": f"{n} is on floor {r['floors']}."}[lang]
    if has_word(q, ["kattal", "m2", "m²", "kvadrat", "size", "площадь", "размер", "razmer"]):
        return {"uz": f"{n} maydoni {r['size_m2']} m².", "ru": f"Площадь {n} — {r['size_m2']} м².",
                "en": f"{n} is {r['size_m2']} m²."}[lang]
    if has_word(q, ["karavot", "yotoq", "bed", "кровать", "кровати"]):
        return {"uz": f"{n}: {r['bed_type']}.", "ru": f"{n}: {r['bed_type']}.", "en": f"{n}: {r['bed_type']}."}[lang]
    if has_word(q, ["necha kishi", "sig'adi", "sigadi", "kishilik", "capacity", "guests", "сколько человек", "вмещ"]):
        return {"uz": f"{n} {r['capacity']} kishigacha sig'adi.", "ru": f"{n} вмещает до {r['capacity']} гостей.",
                "en": f"{n} fits up to {r['capacity']} guests."}[lang]
    return None


# ---------------------------------------------------------------------------
# Mavzular (intent) va ularning javoblari
# ---------------------------------------------------------------------------
# kalit so'zlar: o'zbek / rus / ingliz bir ro'yxatda. Uzunroq ibora — ko'proq ball.
INTENTS: Dict[str, List[str]] = {
    "greeting": ["salom", "assalom", "hayrli", "hello", "hi", "hey", "good morning", "good evening", "привет", "здравствуйте", "добрый"],
    "thanks": ["rahmat", "raxmat", "tashakkur", "thanks", "thank you", "спасибо", "благодарю"],
    "bye": ["xayr", "yaxshi qoling", "yaxshi qolinglar", "salomat bo'ling", "ko'rishguncha", "bye", "goodbye", "see you", "до свидания", "пока"],
    "about_bot": ["sen kim", "siz kim", "kimsan", "kimsiz", "ismin", "who are you", "your name", "ты кто", "кто ты", "как тебя зовут",
                  "nima qila olasan", "nimalarga yordam", "what can you", "yordam ber", "help", "помощь", "что ты умеешь"],
    "booking_how": ["qanday bron", "bron qilaman", "bron qilmoqchi", "bron qilish", "bron qilmoq", "buyurtma", "band qilmoqchi", "xona olmoq", "xona olaman", "joy olmoq",
                    "how to book", "how do i book", "book a room", "make a reservation", "reserve", "забронировать", "бронь", "бронирован", "как забронировать"],
    "price_all": ["narx", "necha pul", "qancha turadi", "price", "prices", "rates", "tarif", "цены", "цена", "стоимость", "сколько стоит"],
    "cheapest": ["eng kam", "minimal", "eng arzon", "arzon xona", "arzonroq", "eng past narx", "cheapest", "cheap", "budget", "самый дешев", "дешев"],
    "premium": ["eng qimmat", "eng yaxshi xona", "eng zo'r", "lyuks", "premium", "most expensive", "luxury", "самый дорог", "люкс"],
    "recommend": ["tavsiya", "qaysi xona", "qaysi biri", "mos xona", "menga xona", "xona kerak", "xona topib", "tanlab ber", "tanlashga",
                  "recommend", "suggest", "which room", "i need a room", "looking for a room", "подскажите номер", "посоветуйте", "какой номер", "нужен номер"],
    "checkin_out": ["check-in", "check in", "checkin", "check-out", "check out", "checkout", "ro'yxatdan o'tish", "kelish vaqti",
                    "qaysi vaqt", "soat nechada", "soat nechgacha", "chiqish", "kirish vaqti", "kirish soati", "vaqti qachon", "qachon kel", "qachon chiq", "nechada", "erta kirish", "kech chiqish", "kechroq", "ertaroq", "заезд", "выезд", "во сколько", "регистрац"],
    "breakfast": ["nonushta", "ovqat", "restoran", "taom", "oshxona", "kechki ovqat", "tushlik", "bar", "breakfast", "restaurant", "food", "dinner",
                  "завтрак", "ресторан", "еда", "питание"],
    "wifi": ["wifi", "wi-fi", "wi fi", "internet", "вайфай", "интернет"],
    "parking": ["parking", "avtoturargoh", "turargoh", "mashina", "avtomobil", "moshina", "garaj", "автостоянка", "парковка", "машин", "car park"],
    "valet": ["valet", "valyet", "mashinamni olib", "mashinani olib", "парковщик", "voller"],
    "welcome": ["kutib olish", "kutib oladi", "kutib oluvchi", "kutib olishadi", "kutib oladimi", "salomlashish", "doorman", "bellboy", "welcome service",
                "встреча", "встречают", "greeting service"],
    "staff": ["xodim", "forma", "kiyim", "uniform", "xizmatchi", "eshik oldi", "персонал", "форма", "сотрудник", "staff"],
    "fountain": ["favvora", "fontan", "fountain", "фонтан"],
    "location": ["manzil", "qayerda", "qayerga", "joylashuv", "lokatsiya", "xarita", "adres", "location", "address", "where is", "map",
                 "адрес", "где находится", "где вы", "как добраться", "yo'l", "metro", "метро"],
    "airport": ["как добраться из аэропорта", "добраться из аэропорта", "aeroport", "samolyot", "airport", "transfer", "taksi", "taxi", "аэропорт", "трансфер", "такси"],
    "floors": ["qavat", "etaj", "floor", "lift", "yulduz", "stars", "этаж", "лифт", "звезд", "xalqaro standart", "nechta qavat"],
    "family": ["oila", "oilam", "bola", "bolalar", "farzand", "beshik", "child", "children", "kids", "family", "baby", "семь", "дет", "ребен"],
    "couples": ["er-xotin", "er xotin", "juftlik", "asal oyi", "xotinim", "erim", "turmush", "couple", "honeymoon", "wife", "husband", "пара", "супруг", "медовый"],
    "accessible": ["nogiron", "aravacha", "wheelchair", "accessible", "disabled", "инвалид", "коляск"],
    "documents": ["hujjat", "pasport", "passport", "nikoh", "guvohnoma", "id karta", "id-karta", "propiska", "document", "documents", "marriage",
                  "certificate", "паспорт", "документ", "свидетельств", "брак"],
    "cancel": ["bekor", "cancel", "qaytadimi", "qaytar", "refund", "pulni qaytar", "отмена", "отменить", "вернуть"],
    "payment": ["to'lov", "tolov", "to'lash", "karta", "naqd", "payment", "pay", "card", "cash", "оплат", "карт", "наличн"],
    "pets": ["hayvon", "mushuk", "kuchuk", "itim", "itimiz", "kuchugim", "mushugim", "pet", "pets", "dog", "cat", "животн", "собак", "кошк"],
    "smoking": ["chekish", "sigaret", "smoking", "smoke", "курить", "курение"],
    "facilities": ["fitnes", "fitness", "sauna", "gym", "spa", "konferensiya", "zal", "conference", "тренажер", "конференц", "сауна"],
    "pool": ["basseyn", "baseyn", "bassein", "hovuz", "suzish", "pool", "swimming", "бассейн"],
    "why": ["nima uchun sizni", "nega sizni", "nima uchun mehmonxonangiz", "afzallik", "nimasi yaxshi", "why choose", "why your hotel", "why should", "почему вы", "преимущества"],
    "review": ["sharh", "baho ber", "reyting", "review", "reviews", "rating", "отзыв", "оценк"],
    "view": ["balkon", "teleminora", "minora", "manzara", "ko'rinish", "view", "balcony", "tower", "балкон", "вид", "башня"],
    "contact": ["telefon", "raqam", "aloqa", "email", "pochta", "contact", "phone", "call", "связаться", "телефон", "позвонить", "kontakt"],
    "complaint": ["shikoyat", "norozi", "muammo", "yoqmadi", "complain", "complaint", "problem", "жалоб", "проблем", "не понравил"],
    "languages": ["qaysi til", "tilda", "tillar", "language", "languages", "speak", "на каком языке", "языки"],
    "business": ["biznes", "xizmat safari", "komandirovka", "business", "ish stoli", "командировк", "деловой"],
    "late_arrival": ["kech keldim", "kech kelsam", "kech kelaman", "kech yetib", "tunda kel", "kechasi kel", "tungi reys", "tunda yetib",
                     "kelsam bo'ladimi", "kelsam mumkinmi", "yetib kelsam", "kelib qolsam", "kech soat",
                     "late arrival", "arrive late", "arriving late", "arrive at night", "поздно приед", "поздно прилет", "ночью приед"],
    "discount": ["chegirma", "aksiya", "skidka", "bonus", "promo", "discount", "special offer", "акци", "скидк"],
    "is_bot": ["robotmisan", "robotmisiz", "botmisan", "botmisiz", "odammisan", "odammisiz", "insonmisiz", "are you a robot", "are you a bot",
               "are you human", "ты бот", "ты робот", "ты человек", "вы бот", "вы робот", "вы человек"],
}

ANSWERS: Dict[str, Dict[str, Optional[str]]] = {
    "greeting": L(
        f"Assalomu alaykum! Men {HOTEL['name']} yordamchisiman. Xona tanlash, narxlar, bron qilish va xizmatlar bo'yicha yordam beraman. Nima qiziq?",
        f"Здравствуйте! Я помощник отеля {HOTEL['name']}. Помогу с выбором номера, ценами, бронированием и услугами. Чем могу помочь?",
        f"Hello! I'm the assistant of {HOTEL['name']}. I can help with rooms, prices, booking and services. What would you like to know?"),
    "thanks": L("Arzimaydi! Yana savol bo'lsa, bemalol yozing 🙂", "Пожалуйста! Если будут вопросы — пишите 🙂", "You're welcome! Ask me anything else 🙂"),
    "bye": L("Xayr! Sizni mehmonxonamizda kutib qolamiz.", "До свидания! Будем рады видеть вас в нашем отеле.", "Goodbye! We look forward to welcoming you."),
    "about_bot": L(
        "Men mehmonxonaning AI yordamchisiman. Quyidagilarga javob bera olaman: xona turlari va narxlar, sizga mos xonani tavsiya qilish, "
        "bron qilish tartibi, kerakli hujjatlar, nonushta va xizmatlar, avtoturargoh/valet, manzil va masofalar, bekor qilish shartlari. "
        "Masalan: «2 kishi, 100$ gacha xona tavsiya qiling».",
        "Я ИИ-помощник отеля. Отвечаю про номера и цены, подбор номера, порядок бронирования, документы, завтрак и услуги, парковку, адрес и условия отмены. "
        "Например: «подберите номер на 2 человек до 100$».",
        "I'm the hotel's AI assistant. I can answer about rooms and prices, recommend a room, explain how to book, required documents, breakfast and services, "
        "parking, location and cancellation. Try: “recommend a room for 2 guests up to 100$”."),
    "late_arrival": L(
        f"Resepshn 24 soat ochiq, shuning uchun kechasi ham kelishingiz mumkin. Check-in {HOTEL['check_in']} dan boshlanadi. Juda kech yetib kelsangiz, oldindan resepshnga xabar bering: {HOTEL['phone']} — xonangiz saqlab qo'yiladi.",
        f"Ресепшн работает круглосуточно, заехать можно и ночью. Заезд с {HOTEL['check_in']}. Если приедете очень поздно, предупредите ресепшн: {HOTEL['phone']} — номер сохранят.",
        f"Reception is open 24/7, so you can arrive at night. Check-in starts at {HOTEL['check_in']}. If you arrive very late, let reception know in advance: {HOTEL['phone']}."),
    "discount": L(
        "Hozircha alohida chegirma tizimi yo'q, lekin narxga nonushta, tezkor Wi-Fi, yopiq avtoturargoh va valet allaqachon kiritilgan. 6 yoshgacha bolalar mavjud karavotda bepul. Maxsus takliflar bo'yicha resepshndan so'rang: " + HOTEL['phone'] + ".",
        "Отдельной системы скидок пока нет, но в цену уже входят завтрак, быстрый Wi-Fi, парковка и валет. Дети до 6 лет — бесплатно. По особым предложениям — на ресепшн: " + HOTEL['phone'] + ".",
        "There is no separate discount system yet, but breakfast, fast Wi-Fi, covered parking and valet are already included. Children under 6 stay free. Ask reception about special offers: " + HOTEL['phone'] + "."),
    "is_bot": L(
        "Men inson emasman, sun'iy intellekt asosidagi yordamchiman. Mehmonxona ma'lumotlari bo'yicha tez javob beraman; murakkab masalalarda resepshn xodimlari yordam beradi: " + HOTEL['phone'] + ".",
        "Я не человек, а ИИ-помощник. Быстро отвечаю по данным отеля; в сложных случаях помогут сотрудники ресепшн: " + HOTEL['phone'] + ".",
        "I'm not a human — I'm an AI assistant. I answer quickly from the hotel's data; for complex matters our reception team will help: " + HOTEL['phone'] + "."),
    "pool": L("Afsuski, mehmonxonada suzish havzasi (basseyn) yo'q. Fitnes zal va sauna 2-qavatda mavjud.", "К сожалению, бассейна в отеле нет. Есть фитнес-зал и сауна на 2 этаже.",
              "Sorry, the hotel has no swimming pool. There is a gym and a sauna on floor 2."),
    "why": L("Bizni tanlash sabablari: markaziy joylashuv (Amir Temur xiyobonidan 270 m), qavatlar mehmon turiga ko'ra ajratilgan (oilalar alohida, tinch qavatda), 24 soat resepshn, nonushta narxga kiritilgan, bepul yopiq avtoturargoh va valet, formadagi xodimlar kutib oladi.",
             "Почему мы: центр города, этажи по типам гостей (семьи отдельно), круглосуточный ресепшн, завтрак и парковка с валетом бесплатно, встреча гостей персоналом в форме.",
             "Why us: central location, floors separated by guest type (families on their own quiet floor), 24/7 reception, breakfast included, free covered parking with valet, uniformed greeters."),
    "review": L("Sharh qoldirish uchun «Xonalar» bo'limida kerakli xonani oching — pastda sharhlar va «Sharh yozish» formasi bor. Sharhingizni AI tahlil qiladi (ijobiy/neytral/salbiy) va xonaning reytingiga qo'shiladi.",
                "Отзыв можно оставить в карточке номера (раздел «Xonalar») — внизу есть форма отзыва; ИИ определяет тональность.",
                "Open a room in the Rooms section and use the review form at the bottom; our AI detects the sentiment of your review."),
    "booking_how": L(
        "Bron qilish 5 qadamda:\n1) «Xonalar» bo'limida kirish va chiqish sanasi, mehmonlar sonini tanlang;\n2) mos xonada «Batafsil» tugmasini bosing;\n"
        "3) ism, email, telefonni kiriting;\n4) shaxsni tasdiqlovchi hujjat turi va raqamini kiriting (er-xotin bo'lsangiz «Biz er-xotinmiz» belgisini qo'yib, nikoh guvohnomasi raqamini ham yozing);\n"
        "5) «Bron qilish» ni bosing — bron kodi (masalan SR-2026-00001) beriladi. To'lov joylashish paytida.\nBronni «Mening bronlarim» bo'limida email orqali ko'rasiz.",
        "Бронирование в 5 шагов:\n1) в разделе «Номера» выберите даты и число гостей;\n2) нажмите «Батафсил» у подходящего номера;\n3) введите имя, email, телефон;\n"
        "4) укажите тип и номер документа (для пары отметьте «Мы супруги» и введите номер свидетельства о браке);\n5) нажмите «Бронировать» — получите код брони. Оплата при заселении.",
        "Booking in 5 steps:\n1) in the Rooms section choose your dates and number of guests;\n2) open the room you like;\n3) enter name, email and phone;\n"
        "4) enter your ID type and number (couples tick “We are a married couple” and add the marriage certificate number);\n5) press Book — you get a booking code. You pay at check-in."),
    "checkin_out": L(
        f"Joylashish {HOTEL['check_in']} dan, chiqish {HOTEL['check_out']} gacha. Erta kirish yoki kech chiqish — mavjudligiga qarab, resepshnga so'rov bilan. Resepshn 24 soat ochiq.",
        f"Заезд с {HOTEL['check_in']}, выезд до {HOTEL['check_out']}. Ранний заезд и поздний выезд — по наличию, по запросу. Ресепшн работает круглосуточно.",
        f"Check-in is from {HOTEL['check_in']}, check-out until {HOTEL['check_out']}. Early check-in or late check-out is subject to availability. Reception is open 24/7."),
    "breakfast": L(
        "Nonushta (shved stoli) har kuni 07:00–10:30, narxga kiritilgan. Restoranda o'zbek va yevropa taomlari, lobby-bar va xonaga ovqat yetkazish (07:00–23:00) bor; bolalar menyusi ham mavjud.",
        "Завтрак (шведский стол) ежедневно 07:00–10:30, включён в цену. Есть ресторан узбекской и европейской кухни, лобби-бар и доставка в номер (07:00–23:00), детское меню.",
        "Breakfast (buffet) is served daily 07:00–10:30 and is included. We also have a restaurant with Uzbek and European dishes, a lobby bar and room service (07:00–23:00)."),
    "wifi": L("Barcha xonalar va umumiy joylarda bepul tezkor Wi-Fi bor.", "Бесплатный быстрый Wi-Fi есть во всех номерах и общих зонах.",
              "Free high-speed Wi-Fi is available in all rooms and public areas."),
    "parking": L(
        "Yopiq yer osti avtoturargoh: 60 o'rin, mehmonlar uchun BEPUL. 5 ta elektromobil quvvatlash joyi, nogironlar uchun 4 ta kengaytirilgan o'rin, video-kuzatuv; avtomobil balandligi 2,1 m gacha. Valet xizmati ham bepul.",
        "Крытая подземная парковка: 60 мест, для гостей БЕСПЛАТНО. 5 мест для зарядки электромобилей, 4 расширенных места для маломобильных гостей, видеонаблюдение. Услуга валет бесплатна.",
        "Covered underground parking: 60 spaces, FREE for guests. 5 EV charging spots, 4 wider accessible spaces, CCTV; height limit 2.1 m. Valet service is free too."),
    "valet": L(
        "Valet: mashinangizni kirish oldida qoldiring — formadagi xodim uni yer osti avtoturargohga olib boradi va so'raganingizda 3–5 daqiqada eshik oldiga olib keladi. Mehmonlar uchun bepul, raqamli kvitansiya beriladi.",
        "Валет: оставьте машину у входа — сотрудник в форме отгонит её на подземную парковку и подаст за 3–5 минут по вашей просьбе. Для гостей бесплатно.",
        "Valet: leave your car at the entrance — a uniformed attendant parks it underground and brings it back within 3–5 minutes on request. Free for guests."),
    "welcome": L(
        "Kutib olish xizmati: 1) eshik oldida doorman mashina eshigini ochadi va kirishgacha kuzatadi; 2) lobbida formadagi xodim salomlashadi, choy/suv taklif qilinadi; "
        "3) bellboy sumkalarni yuk aravachasiga oladi, valet mashinani avtoturargohga olib boradi; 4) resepshnda hujjat tekshirilib, kalit-karta beriladi; 5) bellboy sizni xonagacha kuzatadi. Suratlar saytdagi «Kutib olish» bo'limida.",
        "Встреча гостей: 1) у входа швейцар открывает дверь; 2) в лобби вас приветствуют и предлагают чай/воду; 3) бэллбой берёт багаж, валет паркует машину; 4) на ресепшн проверяют документы и выдают ключ-карту; 5) вас провожают до номера.",
        "Welcome service: 1) a doorman opens your car door; 2) staff greet you in the lobby with tea or water; 3) a bellboy takes your luggage and the valet parks your car; 4) reception checks your ID and gives your key card; 5) the bellboy escorts you to your room."),
    "staff": L(
        "Barcha xodimlar mehmonxona formasida va ismi yozilgan nishon bilan ishlaydi. Eshik oldi xizmatchisi va yuk tashuvchilar — qizil (bordo) forma, oq qo'lqop, qora bosh kiyim; valet — yashil kurtka, oltin tugma; resepshn — qora kostyum. Batafsil «Xodimlar va xizmat» bo'limida.",
        "Все сотрудники носят форму и именной бейдж. Швейцар и бэллбои — красная форма, белые перчатки; валет — зелёная куртка; ресепшн — чёрный костюм.",
        "All staff wear uniforms and name badges: doormen and bellboys wear red uniforms with white gloves, valets green jackets, reception black suits."),
    "fountain": L("Bosh kirish oldida favvorali yashil maydon bor (kechqurun yoritiladi). Undan keyin soyabonli kirish va avtomatik shisha eshiklar.",
                  "Перед главным входом — зелёная площадка с фонтаном (вечером подсвечивается).", "There is a green area with a fountain in front of the main entrance, lit up in the evening."),
    "airport": L(
        "Aeroport masofasi: {airport}. Aeroportdan transfer oldindan buyurtma bilan, 15$ (resepshnga yozing).",
        "До аэропорта: {airport}. Трансфер из аэропорта по предварительному заказу — 15$.",
        "Airport: {airport}. Airport transfer on pre-order costs 15$."),
    "floors": L(
        "Mehmonxona {stars} yulduzli, {floors_above} qavatli (+{floors_below} yer osti avtoturargoh qavati), {elevators} ta lift. Qavatlar toifalar bo'yicha ajratilgan: "
        "2 — moslashgan xonalar; 3 — faqat oilalar (Family); 4 — yakka mehmonlar (Single); 5–6 — juftliklar (Double); 7 — do'stlar (Twin); 8 — Deluxe; 9 — Suite (Junior va Prezident).",
        "Отель {stars}★, {floors_above} этажей (+{floors_below} подземных), {elevators} лифта. Этажи разделены по типам гостей: 3 — семьи, 4 — одиночные гости, 5–6 — пары, 7 — друзья (Twin), 8 — Deluxe, 9 — Suite; 2 — номера для маломобильных гостей.",
        "{stars}-star hotel, {floors_above} floors (+{floors_below} underground), {elevators} lifts. Floors are separated by guest type: 3 — families, 4 — solo guests, 5–6 — couples, 7 — friends (Twin), 8 — Deluxe, 9 — Suites; 2 — accessible rooms."),
    "family": L(
        "Oilalar uchun alohida 3-qavat ajratilgan: faqat oilaviy xonalar (4 kishigacha, 36 m², balkon), tinch, bolalar o'yin burchagi bor. "
        "6 yoshgacha bolalar mavjud karavotda BEPUL, qo'shimcha karavot 15$/kecha, bolalar beshigi bepul. Bolalar menyusi va stuli bor. "
        "Bronda ota-ona er-xotin sifatida joylashsa, nikoh guvohnomasi raqami kiritiladi; bolalar uchun tug'ilganlik guvohnomasi yoki ID ma'lumoti olinadi.",
        "Для семей выделен отдельный 3-й этаж: только семейные номера (до 4 гостей), тихо, есть детская зона. Дети до 6 лет — бесплатно на имеющейся кровати, доп. кровать 15$/ночь, детская кроватка бесплатно.",
        "Families have their own quiet 3rd floor with Family rooms (up to 4 guests). Children under 6 stay free in existing beds, an extra bed is 15$/night, and a cot is free."),
    "couples": L(
        "Juftliklar uchun 5–6-qavatlardagi standart ikki kishilik xona ({p_DBL}$), balkonli Deluxe ({p_DLX}$, king-size) yoki kichik lyuks ({p_JSU}$) mos. "
        "Er-xotin sifatida joylashish uchun NIKOH GUVOHNOMASI kerak: bronda «Biz er-xotinmiz» belgisini qo'yib, guvohnoma raqamini kiriting; joylashishda asli ko'rsatiladi.",
        "Для пар подойдут Double (5–6 этаж), Deluxe с балконом или Junior Suite. Для проживания супругов нужно свидетельство о браке: при бронировании отметьте «Мы супруги» и введите номер.",
        "For couples: Standard Double (floors 5–6), Deluxe with balcony or Junior Suite. Married couples need a marriage certificate: tick “We are a married couple” when booking and enter its number."),
    "accessible": L(
        "2-qavatda 6 ta moslashgan xona bor: eshik 90 sm+, pandussiz kirish, aravachada kirish mumkin bo'lgan dush, tutqichlar, liftga eng yaqin. Avtoturargohda 4 ta kengaytirilgan o'rin. Bronda «Moslashgan xona» (ACC) ni tanlang.",
        "На 2 этаже 6 адаптированных номеров: двери от 90 см, без порогов, душ для коляски, поручни, рядом с лифтом. На парковке 4 расширенных места.",
        "Our 6 accessible rooms are on floor 2: 90 cm+ doors, step-free entry, roll-in shower, grab bars, next to the lift. 4 wider parking spaces."),
    "documents": L(
        "Bron formasida shaxsni tasdiqlovchi hujjat turi (pasport / ID-karta / xalqaro pasport) va raqami majburiy; asli joylashishda ko'rsatiladi. "
        "Er-xotin sifatida joylashsangiz nikoh guvohnomasi raqami ham kerak. Do'stlar, hamkasblar va qarindoshlardan guvohnoma so'ralmaydi. "
        "Chet elliklar xalqaro pasport bilan. 18 yoshgacha bolalar kattalarsiz joylashtirilmaydi. Hujjat raqamini chatga yozmang — faqat bron formasiga.",
        "При бронировании обязательны тип и номер документа (паспорт / ID-карта / загранпаспорт); оригинал предъявляется при заселении. Для проживания как супруги нужно свидетельство о браке. Номер документа не пишите в чате — только в форме.",
        "Booking requires your ID type and number (passport / ID card / foreign passport); show the original at check-in. Couples staying together need a marriage certificate. Please don't type document numbers in chat — only in the booking form."),
    "cancel": L("Bronni check-in sanasidan 24 soat oldin bepul bekor qilish mumkin («Mening bronlarim» bo'limida). Kelmasangiz, ko'pi bilan 1 kecha narxi undirilishi mumkin.",
                "Бесплатная отмена — не позднее чем за 24 часа до заезда (раздел «Мои брони»). При незаезде может быть удержана стоимость 1 ночи.",
                "Free cancellation up to 24 hours before check-in (My bookings section). For a no-show, up to 1 night may be charged."),
    "payment": L("To'lov joylashish paytida bank kartasi yoki naqd pul bilan. Onlayn to'lov hozircha yo'q.", "Оплата при заселении картой или наличными. Онлайн-оплаты пока нет.",
                 "You pay at check-in by card or cash. Online payment is not available yet."),
    "pets": L("Uy hayvonlari qabul qilinmaydi (yo'lboshlovchi xizmat itlari bundan mustasno).", "Домашние животные не принимаются (кроме собак-поводырей).",
              "Pets are not accepted (guide dogs are welcome)."),
    "smoking": L("Barcha xonalar chekilmaydigan; chekish faqat belgilangan joylarda.", "Все номера для некурящих; курение — только в отведённых местах.",
                 "All rooms are non-smoking; smoking is allowed only in designated areas."),
    "facilities": L(
        "Fitnes zal va sauna 2-qavatda; konferensiya zali (80 kishigacha, proyektor va ovoz tizimi) 1-qavatda; biznes burchak (kompyuter, printer) ham bor. Saytdagi «Suratlar» bo'limida zallar va yashil hududlarni ko'rishingiz mumkin.",
        "Фитнес-зал и сауна на 2 этаже, конференц-зал до 80 человек на 1 этаже, бизнес-уголок. Фото — в разделе «Suratlar».",
        "Gym and sauna are on floor 2; a conference hall for up to 80 people is on floor 1; there's also a business corner. See photos in the gallery."),
    "view": L("{view}", "Номера с балконом (Deluxe, Family, Junior Suite, Prezident) выходят на северо-восток: слева — Ташкентская телебашня, справа — парк. См. раздел «Balkondan ko'rinish».",
              "Balcony rooms face north-east: the Tashkent TV Tower is on the left, the park on the right. See the balcony view section."),
    "contact": L(f"Resepshn 24 soat ishlaydi: tel. {HOTEL['phone']}, email {HOTEL['email']}. Tillar: o'zbek, rus, ingliz.",
                 f"Ресепшн круглосуточно: тел. {HOTEL['phone']}, email {HOTEL['email']}.", f"Reception is open 24/7: tel. {HOTEL['phone']}, email {HOTEL['email']}."),
    "complaint": L(f"Noqulaylik uchun uzr so'raymiz. Iltimos, muammoni resepshnga ({HOTEL['phone']}) yoki {HOTEL['email']} ga yozing — tezda hal qilamiz. Sharhni xona oynasidagi «Sharh qoldirish» orqali ham qoldirishingiz mumkin.",
                  f"Приносим извинения. Пожалуйста, сообщите на ресепшн ({HOTEL['phone']}) или на {HOTEL['email']} — мы быстро решим вопрос.",
                  f"We're sorry about that. Please tell reception ({HOTEL['phone']}) or write to {HOTEL['email']} and we'll fix it quickly."),
    "languages": L("Xodimlarimiz o'zbek, rus va ingliz tillarida xizmat ko'rsatadi; bu yordamchi ham shu tillarda javob beradi.",
                   "Персонал говорит по-узбекски, по-русски и по-английски; помощник отвечает на этих языках.", "Our staff speak Uzbek, Russian and English, and so does this assistant."),
    "business": L("Xizmat safari uchun standart yakka xona (4-qavat, {p_SGL}$) yoki Deluxe (8-qavat, {p_DLX}$) qulay: ish stoli, tezkor Wi-Fi, tinch joy. 1-qavatda konferensiya zali (80 kishi) va biznes burchak bor.",
                  "Для командировки подойдут Single ({p_SGL}$) или Deluxe ({p_DLX}$): рабочий стол, быстрый Wi-Fi. Есть конференц-зал на 80 человек и бизнес-уголок.",
                  "For business trips: Standard Single ({p_SGL}$) or Deluxe ({p_DLX}$) with a desk and fast Wi-Fi. A 80-person conference hall and business corner are available."),
}

# Javobdan keyin taklif qilinadigan keyingi savollar (tugma bo'lib chiqadi)
FOLLOW_UPS: Dict[str, Dict[str, List[str]]] = {
    "uz": {
        "greeting": ["Xona narxlari qancha?", "Qanday bron qilaman?", "Oilam uchun xona kerak"],
        "price_all": ["Eng arzon xona qaysi?", "Nonushta narxga kiradimi?", "Qanday bron qilaman?"],
        "cheapest": ["Standart yakka xona haqida", "Qanday bron qilaman?", "Avtoturargoh bormi?"],
        "premium": ["Prezident lyuksi haqida", "Balkondan nima ko'rinadi?", "Qanday bron qilaman?"],
        "recommend": ["Qanday bron qilaman?", "Nonushta bormi?", "Qanday hujjatlar kerak?"],
        "booking_how": ["Qanday hujjatlar kerak?", "Bekor qilish shartlari?", "To'lov qanday?"],
        "checkin_out": ["Nonushta bormi?", "Avtoturargoh bormi?", "Kutib olish xizmati qanday?"],
        "breakfast": ["Wi-Fi bormi?", "Check-in vaqti?", "Xona narxlari qancha?"],
        "parking": ["Valet xizmati qanday?", "Manzil qayerda?", "Kutib olish xizmati qanday?"],
        "valet": ["Avtoturargoh bormi?", "Kutib olish xizmati qanday?", "Xodimlar qanday formada?"],
        "welcome": ["Valet xizmati qanday?", "Check-in vaqti?", "Qanday hujjatlar kerak?"],
        "location": ["Aeroportdan qanday boraman?", "Balkondan nima ko'rinadi?", "Avtoturargoh bormi?"],
        "airport": ["Manzil qayerda?", "Check-in vaqti?", "Qanday bron qilaman?"],
        "documents": ["Er-xotinlar uchun nima kerak?", "Qanday bron qilaman?", "Bekor qilish shartlari?"],
        "couples": ["Deluxe (hashamatli) xona haqida", "Qanday hujjatlar kerak?", "Qanday bron qilaman?"],
        "family": ["Oilaviy xona haqida", "Oilalar qaysi qavatda?", "Nonushta bormi?"],
        "floors": ["Oilalar qaysi qavatda?", "Nogironlar uchun xona bormi?", "Balkondan nima ko'rinadi?"],
        "cancel": ["To'lov qanday?", "Qanday bron qilaman?", "Check-in vaqti?"],
        "pool": ["Fitnes zal bormi?", "Nonushta bormi?", "Xona narxlari qancha?"],
        "why": ["Xona narxlari qancha?", "Oilalar qaysi qavatda?", "Qanday bron qilaman?"],
        "review": ["Xona narxlari qancha?", "Qanday bron qilaman?", "Manzil qayerda?"],
        "view": ["Deluxe (hashamatli) xona haqida", "Manzil qayerda?", "Qanday bron qilaman?"],
        "room": ["Qanday bron qilaman?", "Nonushta bormi?", "Xona narxlari qancha?"],
        "photos": ["Hammom suratlari", "Balkon suratlari", "Xona narxlari qancha?"],
        "default": ["Xona narxlari qancha?", "Qanday bron qilaman?", "Avtoturargoh bormi?"],
    },
    "ru": {"default": ["Сколько стоят номера?", "Как забронировать?", "Есть ли парковка?"]},
    "en": {"default": ["How much are the rooms?", "How do I book?", "Is there parking?"]},
}

OFF_TOPIC_NOTE = {
    "uz": ("Bu savol mehmonxona xizmatlariga tegishli emas ko'rinadi, shuning uchun aniq javob bera olmayman. "
           "Men xonalar va narxlar, bron qilish, hujjatlar, nonushta, avtoturargoh, manzil va boshqa xizmatlar bo'yicha yordam beraman. "
           f"Boshqa savol bo'lsa, resepshn: {HOTEL['phone']} (24 soat)."),
    "ru": ("Не уверен, что смогу точно ответить на этот вопрос. Я помогаю с номерами и ценами, бронированием, документами, завтраком, парковкой, адресом и услугами. "
           f"Остальное — на ресепшн: {HOTEL['phone']} (круглосуточно)."),
    "en": ("I'm not sure I can answer that accurately. I can help with rooms and prices, booking, documents, breakfast, parking, location and services. "
           f"For anything else, call reception: {HOTEL['phone']} (24/7)."),
}
LANG_NOTE = {
    "ru": "Подробный ответ пока доступен на узбекском языке:\n",
    "en": "A detailed answer is currently available in Uzbek:\n",
}


# ---------------------------------------------------------------------------
# Asosiy funksiyalar
# ---------------------------------------------------------------------------
def score_intents(q: str) -> List[Tuple[int, str]]:
    """Har mavzu uchun ball: mos kelgan kalit so'zlar uzunliklari yig'indisi."""
    scores = []
    for name, words in INTENTS.items():
        s = sum(len(w) for w in words if re.search(r"(?<!\w)" + re.escape(w), q))
        if s:
            scores.append((s, name))
    return sorted(scores, reverse=True)


def contains_personal_data(text: str) -> bool:
    """Pasport (AB1234567) yoki karta (16 raqam) raqamiga o'xshash matn bormi?"""
    t = text.replace(" ", "").replace("-", "")
    return bool(re.search(r"[A-Za-z]{2}\d{7}", t) or re.search(r"\d{14,19}", t))


def filters_from_text(q: str) -> dict:
    from ai import parse_request_fallback    # kech import: ai.py ham chatbot.py ni ishlatadi (aylana import bo'lmasin)
    return parse_request_fallback(q)


def _fmt(template: str, **kw) -> str:
    try:
        return template.format(**kw)
    except (KeyError, IndexError):
        return template


def _recommendation(q: str, rooms: list, lang: str) -> str:
    from services import rank_rooms
    f = filters_from_text(q)
    useful = f["guests"] or f["max_price"] or f["room_type"] or f["amenities"] or f["audience"]
    if not useful:
        return {"uz": "Sizga mos xonani topish uchun ayting: nechta mehmon, kechasiga qancha (narx), balkon yoki boshqa talab bormi, kim bilan kelasiz (oila, juftlik, do'stlar, ish safari)?",
                "ru": "Чтобы подобрать номер, подскажите: сколько гостей, бюджет за ночь, нужен ли балкон и с кем вы приедете (семья, пара, друзья, командировка)?",
                "en": "To suggest a room, tell me: how many guests, your budget per night, any needs (balcony etc.) and who you're travelling with (family, couple, friends, business)."}[lang]
    ranked = rank_rooms(rooms, f)
    if f["amenities"]:                                       # qulaylik so'ralgan bo'lsa — faqat shu qulaylik bor xonalar
        with_amenity = [r for r in ranked if set(f["amenities"]) & set(r["amenities"])]
        ranked = with_amenity or ranked
    ranked = ranked[:3]
    if not ranked:
        return {"uz": "Afsuski, bunday talabga to'liq mos xona topilmadi. Narx yoki mehmonlar sonini biroz o'zgartirib ko'ring — men qayta tanlab beraman.",
                "ru": "К сожалению, точного совпадения нет. Попробуйте изменить бюджет или число гостей — подберу снова.",
                "en": "Sorry, no room matches all of that. Try adjusting the budget or guest count and I'll search again."}[lang]
    lines = []
    for r in ranked:
        lines.append(f"• {r['name']} — {money(r['price_per_night'])}/{'kecha' if lang == 'uz' else ('ночь' if lang == 'ru' else 'night')}, "
                     f"{r['capacity']} {'kishigacha' if lang == 'uz' else ('гостей' if lang == 'ru' else 'guests max')}, "
                     f"{r['floors']}-{'qavat' if lang == 'uz' else ('этаж' if lang == 'ru' else 'floor')}")
    head = {"uz": "Sizning talabingizga mos xonalar:\n", "ru": "Подходящие номера:\n", "en": "Rooms that fit your request:\n"}[lang]
    tail = {"uz": "\nBo'sh xonalarni aniq ko'rish uchun «Xonalar» bo'limida sanani tanlang yoki yuqoridagi «AI qidiruv» ga shu gapni yozing.",
            "ru": "\nЧтобы увидеть свободные номера, выберите даты в разделе «Xonalar».",
            "en": "\nPick your dates in the Rooms section to see what's available."}[lang]
    return head + "\n".join(lines) + tail


# ---------------------------------------------------------------------------
# Rasm (surat) savollari: "xonaning rasmi bormi?", "lobby qanday ko'rinadi?"
# Rasmlar hotel_info.GALLERY va bazadagi xonalar (room["images"]) dan olinadi — o'zimizdagi ma'lumot, to'qima emas.
# ---------------------------------------------------------------------------
PHOTO_WORDS = ["rasm", "surat", "foto", "photo", "picture", "image", "galere", "gallery", "фото", "картин", "снимк",
               "qanday ko'rinadi", "qanday ko'rinar", "ko'rsating", "ko'rsat", "ko'rmoqchi", "how does it look", "look like", "покажите", "выглядит"]

# (mavzu, kalit so'zlar, GALLERY bo'limi yoki None, xona rasmi izohidagi so'zlar)
PHOTO_TOPICS = [
    ("lobby", ["lobby", "resepshn", "reception", "лобби", "ресепшн"], "Lobby", []),
    ("restaurant", ["restoran", "oshxona", "nonushta", "taom", "ovqat", "restaurant", "kitchen", "breakfast", "ресторан", "кухн", "завтрак"], "Restoran va oshxona", []),
    ("bath", ["hammom", "vanna", "dush", "bath", "shower", "ванн", "душ"], None, ["hammom", "dush"]),
    ("balcony", ["balkon", "manzara", "balcony", "view", "балкон", "вид"], None, ["balkon", "manzara", "ko'rinish"]),
    ("garden", ["bog'", "hovli", "favvora", "spa", "garden", "fountain", "сад", "двор", "фонтан"], "Yashil hudud", []),
    ("hall", ["zal", "konferensiya", "banket", "hall", "conference", "зал", "конференц"], "Zallar", []),
    ("corridor", ["yo'lak", "koridor", "corridor", "hallway", "коридор"], "Yo'laklar", []),
    ("building", ["bino", "fasad", "tashqi", "exterior", "building", "facade", "здани", "фасад"], "Bino va kirish", []),
    ("park", ["xiyobon", "park", "парк"], "Atrofdagi xiyobon", []),
    ("parking", ["avtoturargoh", "turargoh", "parking", "парковк"], "Avtoturargoh", []),
    ("bedroom", ["yotoqxona", "karavot", "bedroom", "bed", "спальн", "кроват"], None, ["yotoqxona", "mehmon zonasi", "mehmonxona zonasi"]),
]
PHOTO_LABEL = {
    "lobby": {"uz": "lobby", "ru": "лобби", "en": "the lobby"},
    "restaurant": {"uz": "restoran va oshxona", "ru": "ресторана и кухни", "en": "the restaurant and kitchen"},
    "bath": {"uz": "hammom", "ru": "ванных комнат", "en": "the bathrooms"},
    "balcony": {"uz": "balkon va manzara", "ru": "балкона и вида", "en": "the balcony and the view"},
    "garden": {"uz": "bog' va hovli", "ru": "сада и двора", "en": "the garden and courtyard"},
    "hall": {"uz": "zallar", "ru": "залов", "en": "the halls"},
    "corridor": {"uz": "yo'laklar", "ru": "коридоров", "en": "the corridors"},
    "building": {"uz": "bino", "ru": "здания", "en": "the building"},
    "park": {"uz": "atrofdagi xiyobon", "ru": "парка рядом", "en": "the nearby park"},
    "parking": {"uz": "avtoturargoh", "ru": "парковки", "en": "the parking"},
    "bedroom": {"uz": "yotoqxonalar", "ru": "спален", "en": "the bedrooms"},
}
PHOTO_MAX = 6


def is_photo_question(q: str) -> bool:
    return has_word(q, PHOTO_WORDS)


def _uniq(items: List[dict], limit: int = PHOTO_MAX) -> List[dict]:
    seen, out = set(), []
    for it in items:
        if it.get("src") and it["src"] not in seen:
            seen.add(it["src"])
            out.append({"src": it["src"], "caption": it.get("caption", "")})
        if len(out) >= limit:
            break
    return out


def photo_selection(q: str, rooms: list) -> Tuple[str, str, List[dict]]:
    """Savolga mos suratlar: (tur, sarlavha, suratlar). Tur: 'room' | mavzu nomi | 'general'."""
    room = find_room(q, rooms)
    if room:
        imgs = _uniq(room.get("images") or ([{"src": room["image_url"], "caption": room["name"]}] if room.get("image_url") else []))
        return "room", room["name"], imgs
    for topic, words, group, room_words in PHOTO_TOPICS:
        if not has_word(q, words):
            continue
        if group:
            imgs = [g for g in hotel_info.GALLERY if g["group"] == group]
        else:
            imgs = [i for r in rooms for i in (r.get("images") or []) if any(w in i.get("caption", "").lower() for w in room_words)]
        imgs = _uniq([{"src": g.get("src"), "caption": g.get("caption", "")} for g in imgs])
        if imgs:
            return topic, topic, imgs
    # umumiy: bir nechta xona + lobby + restoran + bog'
    general = [{"src": r["image_url"], "caption": r["name"]} for r in rooms[:3] if r.get("image_url")]
    for group in ("Lobby", "Restoran va oshxona", "Yashil hudud"):
        first = next((g for g in hotel_info.GALLERY if g["group"] == group), None)
        if first:
            general.append({"src": first["src"], "caption": first["caption"]})
    return "general", "", _uniq(general)


def photo_reply(question: str, rooms: list) -> Optional[Tuple[str, List[dict]]]:
    """Savol rasm haqida bo'lsa (javob matni, suratlar) qaytaradi; aks holda None."""
    lang = detect_lang(question)
    q = normalize(question).strip()
    if not is_photo_question(q):
        return None
    if has_word(q, INTENTS["pool"]):                       # hovuz yo'q — suratini ham ko'rsatib bo'lmaydi
        return ANSWERS["pool"][lang], []
    kind, title, imgs = photo_selection(q, rooms)
    if not imgs:
        return {"uz": f"Hozircha bu mavzuda surat topilmadi. Barcha suratlar saytdagi «Galereya» bo'limida; savol bo'lsa, resepshn: {HOTEL['phone']}.",
                "ru": f"Фото по этой теме пока нет. Все фото — в разделе «Галерея» на сайте; вопросы — ресепшн: {HOTEL['phone']}.",
                "en": f"I have no photos on this topic yet. See the Gallery section on the site, or call reception: {HOTEL['phone']}."}[lang], []
    caps = "; ".join(dict.fromkeys(i["caption"] for i in imgs if i["caption"]))      # takroriy izohlar bir marta
    if kind == "room":
        text = {"uz": f"Mana «{title}» xonasining suratlari: {caps}.",
                "ru": f"Вот фото номера «{title}»: {caps}.",
                "en": f"Here are photos of the {title} room: {caps}."}[lang]
    elif kind == "general":
        text = {"uz": "Mana mehmonxonamizdan bir nechta surat: xonalar, lobby, restoran va hovli. Boshqa joylar suratini ham so'rashingiz mumkin (hammom, balkon, zallar, avtoturargoh). To'liq to'plam saytdagi «Galereya» bo'limida.",
                "ru": "Вот несколько фото нашего отеля: номера, лобби, ресторан и двор. Можно спросить и про другие места (ванная, балкон, залы, парковка). Полная подборка — в разделе «Галерея».",
                "en": "Here are some photos of our hotel: rooms, lobby, restaurant and courtyard. You can also ask about other places (bathroom, balcony, halls, parking). The full set is in the Gallery section."}[lang]
    else:
        label = PHOTO_LABEL[kind][lang]
        text = {"uz": f"Mana {label} suratlari: {caps}.",
                "ru": f"Вот фото {label}: {caps}.",
                "en": f"Here are photos of {label}: {caps}."}[lang]
    return text, imgs


def photo_images(question: str, rooms: list) -> List[dict]:
    """Chat javobiga qo'shiladigan suratlar (rasm savoli bo'lmasa — bo'sh ro'yxat)."""
    res = photo_reply(question, rooms)
    return res[1] if res else []


def reply(question: str, history: Optional[List[dict]], rooms: list) -> Tuple[str, List[str]]:
    """
    Savolga javob va keyingi savol takliflarini qaytaradi.
    history — oldingi xabarlar (oxirgisi — hozirgi savol bo'lishi mumkin); kontekst uchun ishlatiladi.
    """
    history = history or []
    lang = detect_lang(question)
    q = normalize(question).strip()
    sug = FOLLOW_UPS.get(lang, FOLLOW_UPS["uz"])

    if contains_personal_data(question):
        warn = {"uz": "Xavfsizlik uchun pasport yoki karta raqamini chatga yozmang. Hujjat raqami faqat bron formasida kiritiladi va faqat oxirgi 3 raqami ko'rsatiladi.",
                "ru": "В целях безопасности не пишите в чат номера паспорта и карты — только в форме бронирования.",
                "en": "For your safety, please don't type passport or card numbers in chat — use the booking form only."}[lang]
        return warn, sug.get("default", FOLLOW_UPS["uz"]["default"])

    photo = photo_reply(question, rooms)
    if photo:
        return photo[0], sug.get("photos", sug["default"])

    scores = score_intents(q)
    top = scores[0][1] if scores else None
    named_room = find_room(q, rooms)

    # "Prezident kim?" — bu davlat rahbari haqidagi savol, "Prezident lyuksi" xonasi emas: mavzudan tashqari
    if named_room and named_room.get("code") == "PRS" and has_word(q, ["kim", "kimdir", "who", "кто"]) and \
            not has_word(q, ["lyuks", "suite", "xona", "narx", "qancha", "rasm", "room", "price", "номер"]):
        return OFF_TOPIC_NOTE[lang], sug.get("default", FOLLOW_UPS["uz"]["default"])

    # 1) aniq xona nomi aytilgan
    if named_room and top not in ("floors", "documents", "cancel"):
        attr = room_attribute(named_room, q, lang)
        text = attr or room_summary(named_room, lang)
        return text, sug.get("room", sug["default"])

    # 2) qisqa davomiy savol ("narxi qancha?", "va qavati?") — oldingi xonaga murojaat
    prev_room = None
    user_turns = [m for m in history if m.get("role") == "user" and m.get("content") != question][-2:]   # faqat oxirgi 2 ta foydalanuvchi xabari
    for m in reversed(user_turns):
        prev_room = find_room(normalize(m.get("content", "")), rooms)
        if prev_room:
            break
    generic = has_word(q, ["narxlar", "barcha", "hamma", "xonalar", "prices", "all", "цены", "все"])
    if prev_room and not generic and len(q.split()) <= 4:
        attr = room_attribute(prev_room, q, lang)
        if attr:
            return attr, sug.get("room", sug["default"])

    # 3) tavsiya (mehmon soni/narx/talab aytilgan)
    f = filters_from_text(q)
    any_filter = f["guests"] or f["max_price"] or f["amenities"] or f["room_type"] or f["audience"]
    wants_rec = top == "recommend" or (not scores and any_filter) or \
        (top in ("price_all", "cheapest", "business", "couples", "family", "view") and (f["guests"] or f["max_price"]))
    if wants_rec:
        return _recommendation(q, rooms, lang), sug.get("recommend", sug["default"])

    if not top:
        return OFF_TOPIC_NOTE[lang], sug.get("default", FOLLOW_UPS["uz"]["default"])

    # 4) maxsus mavzular — ma'lumotdan hisoblanadi
    cheapest = min(rooms, key=lambda r: r["price_per_night"]) if rooms else None
    priciest = max(rooms, key=lambda r: r["price_per_night"]) if rooms else None
    if top == "cheapest" and cheapest:
        text = {"uz": f"Eng arzon xonamiz — {cheapest['name']}: kechasiga {money(cheapest['price_per_night'])} ({cheapest['size_m2']} m², {cheapest['floors']}-qavat). Nonushta narxga kiritilgan.",
                "ru": f"Самый доступный номер — {cheapest['name']}: {money(cheapest['price_per_night'])} за ночь. Завтрак включён.",
                "en": f"Our cheapest room is {cheapest['name']}: {money(cheapest['price_per_night'])} per night. Breakfast is included."}[lang]
    elif top == "premium" and priciest:
        text = {"uz": f"Eng yuqori toifa — {priciest['name']}: kechasiga {money(priciest['price_per_night'])} ({priciest['size_m2']} m², {priciest['floors']}-qavat; 2 yotoqxona, jakuzi, panoramali manzara).",
                "ru": f"Самый престижный номер — {priciest['name']}: {money(priciest['price_per_night'])} за ночь.",
                "en": f"Our top room is the {priciest['name']}: {money(priciest['price_per_night'])} per night."}[lang]
    elif top == "price_all":
        head = {"uz": "Narxlar (kechasiga, nonushta bilan):\n", "ru": "Цены за ночь (с завтраком):\n", "en": "Prices per night (breakfast included):\n"}[lang]
        text = head + "\n".join(f"• {r['name']} — {money(r['price_per_night'])}" for r in rooms)
    elif top == "airport":
        d = next((x for x in hotel_info.DISTANCES if "aeroport" in x["place"].lower()), None)
        text = _fmt(ANSWERS["airport"][lang] or ANSWERS["airport"]["uz"], airport=d["value"] if d else "~6 km")
    elif top == "location":
        near = "; ".join(f"{x['place']} — {x['value']}" for x in hotel_info.DISTANCES[:3])
        text = {"uz": f"{HOTEL['name']}: {HOTEL['address']}. {near}. Aniq nuqta va xarita — saytning «Manzil» bo'limida.",
                "ru": f"{HOTEL['name']}: {HOTEL['address']}. Расстояния: {near}. Карта — в разделе «Manzil».",
                "en": f"{HOTEL['name']}: {HOTEL['address']}. Distances: {near}. See the map in the Location section."}[lang]
    elif top == "view":
        text = (ANSWERS["view"][lang] if lang != "uz" else
                f"Balkonli xonalar (Deluxe, oilaviy xona, kichik lyuks, Prezident lyuksi) {hotel_info.BALCONY_VIEW['direction']} tomonga qaraydi: "
                f"balkondan chap tomonda {hotel_info.BALCONY_VIEW['left']}, o'ng tomonda {hotel_info.BALCONY_VIEW['right']}.")
    elif top == "floors" and has_word(q, ["oila", "oilam", "bola", "family", "farzand", "семь", "дет"]):
        text = ANSWERS["family"][lang] or ANSWERS["family"]["uz"]
    else:
        ans = ANSWERS.get(top, {})
        text = ans.get(lang)
        if text is None:                                           # ru/en tarjimasi yo'q — o'zbekcha javob
            text = LANG_NOTE.get(lang, "") + (ans.get("uz") or OFF_TOPIC_NOTE["uz"])
        h = HOTEL
        prices = {f"p_{r['code']}": r["price_per_night"] for r in rooms}
        text = _fmt(text, stars=h["stars"], floors_above=h["floors_above"], floors_below=h["floors_below"], elevators=h["elevators"],
                    view="", airport="", **prices)
    return text, sug.get(top, sug["default"])


def suggestions_for(question: str, history: Optional[List[dict]] = None, rooms: Optional[list] = None) -> List[str]:
    """AI javob bergan holda ham keyingi savol takliflarini berish uchun."""
    return reply(question, history, rooms or [])[1]
