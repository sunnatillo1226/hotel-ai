# Silk Road Grand Hotel — AI bilan xona bron qilish tizimi

Mehmonxona xonalarini onlayn bron qilish sayti. Sun'iy intellekt (Hugging Face) 3 joyda ishlaydi.

## 1. Loyiha nima qiladi?

**Mehmon uchun:**
- Sana, mehmonlar soni va xona turi bo'yicha bo'sh xonalarni qidirish
- **AI qidiruv:** "Oilam bilan 4 kishi, balkonli xona kerak, 160$ gacha" deb oddiy gap yozsa, AI shuni tushunib, mos xonalarni topadi
- **Bino (haqiqiy suratlar):** 9 qavat, favvorali kirish, yer osti avtoturargoh. **Qavatlar toifalar bo'yicha ajratilgan** (3-qavat — faqat oilalar, 4 — yakka mehmonlar, 5–6 — juftliklar, 7 — do'stlar, 8 — Deluxe, 9 — Suite, 2 — moslashgan xonalar); qavatni bossangiz, u yerda nima borligi chiqadi
- **Kutib olish xizmati** (5 bosqich, suratlar bilan), **suratlar galereyasi** (lobby, yo'lak, restoran, oshxona, zal, yashil hudud, xiyobon), **balkondan ko'rinish** (chapda teleminora, o'ngda xiyobon), **xarita** (OpenStreetMap) va koordinatalardan hisoblangan masofalar
- Har bir xona turida **ko'p surat** (yotoqxona, hammom/dush, balkon, yo'lak)
- **Xodimlar va forma**, valet xizmati (mashinani olib borish va olib kelish)
- **"Kimlar uchun?"** filtri: yolg'iz, er-xotin, do'stlar, oila, biznes, nogironligi bo'lgan mehmonlar, VIP
- Mehmonxona haqida: bino tuzilishi, joylashuv, qulayliklar, avtoturargoh, **bron uchun hujjatlar** (bronda pasport/ID turi va raqami majburiy; er-xotinlardan nikoh guvohnomasi raqami so'raladi)
- Xonani bron qilish (tur bo'yicha "Qolgan: N xona"), bronni email orqali ko'rish va bekor qilish
- **AI chat yordamchi:** narx, nonushta, check-in vaqti va boshqa savollarga javob beradi
- Sharh qoldirish — **AI sharh ijobiy yoki salbiy ekanini avtomatik aniqlaydi**

**Real hayotga yaqin qoidalar:** bron kodi (`SR-2026-00001`), shu turdagi barcha xonalar band bo'lsa bron qilib bo'lmaydi (lekin bir mehmon chiqqan kuni ikkinchisi kirishi mumkin), eng ko'pi 30 kecha, eng ko'pi 1 yil oldin, sig'imdan ko'p mehmon mumkin emas.

**Admin uchun** (`admin.html`): bronlar soni, tushum, bugungi bandlik foizi, sharhlar kayfiyati, barcha bronlar ro'yxati.

## 2. Texnologiyalar va nima uchun

| Qism | Texnologiya | Qayerda ishlaydi |
|---|---|---|
| Sayt (frontend) | HTML + CSS + JavaScript | **Netlify** |
| Server (backend) | Python **FastAPI** | **Railway** |
| Baza | SQLAlchemy orqali: lokalda **SQLite**, Railway'da **PostgreSQL** | Railway |
| Sun'iy intellekt | **Hugging Face** Inference API (model: `Qwen/Qwen3-8B`) | Hugging Face |

Frontend va backend alohida joylarda turadi. Ular bir-biri bilan `fetch` orqali JSON almashadi (REST API).

## 3. Fayllar tuzilishi

```
hotel-ai/
├── backend/                 ← server qismi
│   ├── main.py              ← barcha API manzillar (endpointlar)
│   ├── models.py            ← baza jadvallari (Room, Booking, Review)
│   ├── schemas.py           ← kiruvchi/chiquvchi ma'lumot shakli va tekshiruvi (Pydantic)
│   ├── services.py          ← qoidalar: band-bo'shligini tekshirish, narx hisoblash, xonalarni baholash
│   ├── ai.py                ← AI: Hugging Face chat, matndan filtr ajratish, sharh kayfiyati (+ zaxira rejim)
│   ├── chatbot.py           ← suhbat mexanizmi: til aniqlash (uz/ru/en), mavzu ballari, xona haqida javob, tavsiya, keyingi savol takliflari
│   ├── database.py          ← bazaga ulanish
│   ├── seed.py              ← 8 xona turi (jami 84 xona) va 6 ta sharh
│   ├── hotel_info.py        ← mehmonxona profili: bino, joylashuv, qulayliklar, hujjatlar (sayt va AI shundan oladi)
│   ├── tests/               ← avtomatik testlar (pytest, 55 ta)
│   ├── benchmark.py         ← tezlikni o'lchash skripti
│   ├── requirements.txt     ← kerakli kutubxonalar
│   ├── requirements-dev.txt ← test uchun qo'shimcha kutubxonalar
│   ├── Procfile             ← Railway serverni qanday ishga tushirishi
│   └── .env.example         ← sozlamalar namunasi
└── frontend/                ← sayt qismi
    ├── index.html           ← asosiy sahifa
    ├── app.js               ← saytning mantig'i (qidiruv, bron, chat)
    ├── style.css            ← ko'rinish
    ├── admin.html           ← admin panel
    ├── img/                 ← namunaviy suratlar, mavzu bo'yicha papkalarda: bino, lobbi, xonalar, hammom, restoran...; mualliflar: img/MUALLIFLAR.md
    ├── config.js            ← backend manzili (deploydan keyin o'zgartiriladi)
    ├── tests/smoke.js       ← sayt testi (45 tekshiruv)
    └── netlify.toml         ← Netlify sozlamasi (kesh va xavfsizlik sarlavhalari)
```

**`docs/`** papkasi — "Dasturiy injiniringga kirish" fani uchun hujjatlar:
`01-talablar.md` (SRS, jarayon modeli, xavflar) · `02-loyihalash.md` (arxitektura, use-case, ER, ketma-ketlik diagrammalari) · `03-test-hisoboti.md` · `04-samaradorlik-hisoboti.md` · **`05-mehmonxona-standartlari.md`** (xona turlari, kimlar uchun, standartlar, hujjatlar) · **`06-fayllar-xaritasi.md`** (qaysi fayl nima qiladi)

## 4. Lokal kompyuterda ishga tushirish

**Eng oson yo'l (PyCharm):** `main.py` ni oching va yashil ▶ (Run) tugmasini bosing — u kutubxonalarni o'zi o'rnatadi, backend (8000) va saytni (5500) yoqadi va brauzerda ochadi. To'xtatish: qizil ■. (Windows'da `ishga_tushir.bat` ham xuddi shuni qiladi.) Quyida qo'lda bajarish yo'li:

**Eng oson yo'l (Windows):** loyiha papkasidagi `ishga_tushir.bat` fayliga ikki marta bosing — u kutubxonalarni o'rnatadi, ikkala serverni yoqadi va saytni brauzerda ochadi (PyCharm'ning `.venv` muhiti kerak). Qo'lda ishga tushirish quyida.

**Birinchi terminal (backend):**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Server `http://127.0.0.1:8000` da ishlaydi. Avtomatik hujjat: `http://127.0.0.1:8000/docs`.
Birinchi ishga tushganda baza (`hotel.db`) va xonalar o'zi yaratiladi.
> Eski versiyadan qolgan `hotel.db` bo'lsa, uni o'chiring (server shuni aytib to'xtaydi) — yangi baza o'zi yaratiladi.

**Ikkinchi terminal (frontend):**
```bash
cd frontend
python -m http.server 5500
```
Brauzerda oching: `http://localhost:5500`

**Haqiqiy AI'ni yoqish (ixtiyoriy):**
1. https://huggingface.co/settings/tokens da yangi token yarating (ruxsat: *Make calls to Inference Providers*).
2. `backend/.env.example` faylini `.env` deb nusxalang va `HF_TOKEN=` dan keyin tokenni yozing.
3. Serverni qayta ishga tushiring. Sayt pastida "AI faol" yozuvi chiqadi.

Token bo'lmasa ham sayt to'liq ishlaydi: AI o'rniga oddiy qoidalarga asoslangan **zaxira rejim** ishlaydi (chatda javob tagida "tayyor javob" yoziladi).

## 5. Testlar va tezlik

```bash
cd backend
pip install -r requirements-dev.txt
pytest -v              # 55 ta avtomatik test
python benchmark.py    # tezlik o'lchovi (150 xona, 3000 bron)
```
Sayt testi (backend ishlab turganda): `cd frontend/tests && npm install jsdom && node smoke.js`

**Tezlik natijasi** (batafsil: `docs/04-samaradorlik-hisoboti.md`), 150 xonali sinov bazasida:

| So'rov | Oldin | Keyin |
|---|---|---|
| Xonalar ro'yxati (sana bilan) | 168 ms | 10 ms |
| AI qidiruv | 126 ms | 8 ms |
| Ro'yxat javobi tarmoqda | 34.5 KB | 2.2 KB |

Sabablari: ko'p so'rovni bittaga birlashtirish (N+1 muammosi), bazada indekslar, gzip siqish.
Bu raqamlar server ichida o'lchangan; haqiqiy tarmoq va AI javob vaqti qo'shilmagan (hisobotda yozilgan).

## 6. Internetga chiqarish (deploy)

**Backend → Railway**
1. Loyihani GitHub'ga yuklang (`.env` va `hotel.db` `.gitignore` da, yuklanmaydi).
2. railway.app → *New Project* → *Deploy from GitHub repo* → shu repo.
3. Service sozlamalarida **Root Directory = `backend`** qiling.
4. Loyihaga *New → Database → PostgreSQL* qo'shing, so'ng backend servisining *Variables* bo'limida `DATABASE_URL` ni PostgreSQL'ga ulang (Railway'da "Add reference" tugmasi bor).
5. Yana qo'shing: `HF_TOKEN`, `ADMIN_KEY` (o'zingiz o'ylab topgan parol), `ALLOWED_ORIGINS` (keyingi qadamda olinadigan Netlify manzili).
6. *Settings → Networking → Generate Domain* bosing. Manzil shunga o'xshaydi: `https://xxxx.up.railway.app`. `/api/health` ni ochib tekshiring.

**Frontend → Netlify**
1. `frontend/config.js` ichida `API_URL` ni Railway manzilingizga almashtiring.
2. netlify.com → *Add new site* → GitHub'dan import qiling, **Base directory = `frontend`**. (Yoki `frontend` papkasini sudrab tashlash orqali ham joylash mumkin.)
3. Netlify bergan manzilni Railway'dagi `ALLOWED_ORIGINS` ga yozing (CORS shuni talab qiladi).

## 7. Himoya uchun: ustoz berishi mumkin bo'lgan savollar

**Baza qaysi va nima uchun?**
SQLAlchemy ORM orqali ishlaydi. Lokalda SQLite (oddiy fayl, o'rnatish shart emas), Railway'da PostgreSQL. Kod o'zgarmaydi, faqat `DATABASE_URL` o'zgaradi (`database.py`). 3 ta jadval: `rooms`, `bookings`, `reviews`. `bookings` va `reviews` jadvali `room_id` orqali `rooms` bilan bog'langan (foreign key).

**Backend qaysi qism?**
`backend/` papkasi, FastAPI. `main.py` — so'rovlarni qabul qiladigan manzillar. `services.py` — qoidalar (masalan, band-bo'shlik). `ai.py` — sun'iy intellekt. Shu bo'lishning sababi: har fayl bitta ishni qiladi, kodni topish va tushuntirish oson.

**Xona bandligi qanday tekshiriladi?**
Har xona turidan bir nechta bor (`quantity`). `services.py` → `peak_occupancy` so'ralgan sanalardagi har kecha uchun band xonalar sonini hisoblaydi (kesishish sharti: `eski.check_in < yangi.check_out` va `eski.check_out > yangi.check_in`). Eng band kechada `quantity − band > 0` bo'lsa, tur bo'sh. Bekor qilingan bronlar hisobga olinmaydi.

**AI qayerda ishlatilgan?** (`ai.py`)
1. `chat_answer` — chat. AI'ga muloqot qoidalari (foydalanuvchi tilida, qisqa, to'qimasdan, noaniq savolda aniqlashtirish, shaxsiy ma'lumot so'ramaslik), mehmonxona ma'lumoti va bazadagi xonalar ro'yxati beriladi, shuning uchun o'zidan narx to'qib chiqarmaydi.
2. `parse_request` — erkin matnni JSON filtrga aylantiradi (necha kishi, narx, tur, qulayliklar). So'ng `services.rank_rooms` har xonaga ball berib saralaydi.
3. `analyze_sentiment` — sharh kayfiyatini aniqlaydi (ijobiy / neytral / salbiy), admin panelda statistika chiqadi.

**AI ishlamay qolsa-chi?**
`hf_chat` xato bo'lsa `None` qaytaradi, dastur esa `chatbot.py` ga o'tadi: u tilni aniqlaydi (o'zbek/rus/ingliz), savol mavzusini ball bilan tanlaydi, xona nomi aytilsa shu xona haqida javob beradi, "va qavati?" kabi qisqa savolda oldingi xonani eslaydi, "2 kishi, 100$ gacha" kabi talabda xona tavsiya qiladi va har javobdan keyin 3 ta keyingi savol tugmasini qaytaradi. Pasport/karta raqami yozilsa, uni AI'ga yubormaydi va ogohlantiradi. Sayt hech qachon AI sababli to'xtamaydi.

**Frontend backend bilan qanday gaplashadi?**
`app.js` dagi `api()` funksiyasi `fetch` bilan backendga so'rov yuboradi, backend JSON qaytaradi. Backend manzili `config.js` da turadi.

**Xavfsizlik qanday?**
- Kiruvchi ma'lumot Pydantic bilan tekshiriladi (email shakli, sana, mehmonlar soni, reyting 1–5).
- SQLAlchemy parametrli so'rov ishlatadi, shuning uchun SQL injection xavfi yo'q.
- Saytda foydalanuvchi matni `esc()` funksiyasi orqali chiqariladi (XSS'dan himoya).
- Bronni faqat o'sha email egasi bekor qila oladi.
- Admin API'lari `X-Admin-Key` sarlavhasi bilan himoyalangan; token va parollar `.env` da, GitHub'ga yuklanmaydi.

**Saytni tezlashtirish uchun nima qilindi?**
Eng muhimi — N+1 muammosini bartaraf etish: oldin har xona uchun alohida so'rov ketardi, endi hammasi 2 ta so'rovda (`services.rooms_to_dicts`). Bundan tashqari: bazada indekslar (`models.py`), gzip siqish (`main.py`), AI uchun kutish chegarasi (`ai.py`), saytda yuklanish "skeleti" va brauzer keshi (`netlify.toml`).

**Qulaylik uchun nima qilindi?**
Telefonga moslashuvchan dizayn, klaviatura bilan boshqarish (Tab, Esc), fokus ramkasi, o'qiladigan kontrast, tushunarli xato xabarlari, sana va narxni avtomatik hisoblash, yuklanish holati, avtomatik to'ldirish (`autocomplete`) maydonlari.

**Mehmonxona real standartlarga mosmi?**
Bu o'quv (namunaviy) mehmonxona. U Hotelstars Union 4 yulduz mezonlari va O'z DSt 3296:2018 ga *moslab loyihalangan*, lekin rasmiy sertifikatlanmagan. Batafsil, mezonma-mezon jadval: `docs/05-mehmonxona-standartlari.md`.

**Hozircha nimalar yo'q? (halol aytish yaxshi)**
To'lov tizimi, email orqali tasdiqlash, har bir mehmon uchun alohida login. Admin himoyasi oddiy kalit asosida; keyingi qadam JWT login.

## 8. Ish rejasi (4 bosqich)

1. **Poydevor:** baza, API, qoidalar. *(bajarilgan)*
2. **Sayt va AI:** frontend, admin panel, AI ulash, lokal sinov. *(bajarilgan; haqiqiy HF tokeni bilan sinash qoldi)*
3. **Tezlik, qulaylik, testlar, hujjatlar** *(bajarilgan)*
4. **Deploy:** GitHub, Railway (backend + PostgreSQL), Netlify, jonli sinov. Keyin sayqal: kuchliroq admin login, savol-javob mashqi.
