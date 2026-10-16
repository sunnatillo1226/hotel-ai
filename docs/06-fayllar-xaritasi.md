# 6. Fayllar xaritasi — qaysi fayl nima uchun?

Ustoz "bu qism qayerda?" deb so'rasa, shu jadvaldan toping. Har bir faylning yuqorisida ham o'zining izohi yozilgan.

## Backend (`backend/`) — server, Python (FastAPI)
| Fayl | Nima haqida | Savol bo'lsa nima deysiz |
|---|---|---|
| `main.py` | Barcha API manzillar (xonalar, bron, sharh, AI, admin, mehmonxona profili) | "So'rovlarni qabul qiladigan joy" |
| `models.py` | Baza jadvallari: `Room` (xona turi), `Booking` (bron), `Review` (sharh) + indekslar | "Baza tuzilishi shu yerda" |
| `schemas.py` | Kiruvchi/chiquvchi ma'lumot shakli va tekshiruvi (Pydantic) | "Noto'g'ri ma'lumotni shu yer to'xtatadi" |
| `services.py` | Qoidalar: band-bo'shlik (`peak_occupancy`), narx, reyting, xonalarni saralash | "Biznes mantiq" |
| `ai.py` | AI: Hugging Face chat, matndan filtr ajratish, sharh kayfiyati | "Hugging Face shu faylda" |
| `chatbot.py` | Suhbat mexanizmi (AI yo'q paytda ham): til, mavzu, xona, tavsiya, takliflar | "Chat qanday javob beradi" |
| `hotel_info.py` | Mehmonxona ma'lumoti: bino, qavatlar, favvora, valet, xodimlar, qulayliklar, hujjatlar | "Yagona ma'lumot manbai" |
| `seed.py` | Boshlang'ich 8 xona turi (84 xona) va sharhlar | "Baza bo'sh bo'lsa to'ldiradi" |
| `database.py` | Bazaga ulanish (SQLite lokal, PostgreSQL Railway'da) | "Baza qaysi? — shu yerda almashadi" |
| `benchmark.py` | Tezlik o'lchash (150 xona, 3000 bron) | "Tezlikni shunday o'lchadik" |
| `tests/conftest.py` | Testlar uchun toza vaqtinchalik baza | |
| `tests/test_api.py` | 27 ta avtomatik test | "Tizim ishlashini shunday tekshirdik" |
| `requirements.txt`, `requirements-dev.txt` | Kutubxonalar ro'yxati (ishlash / test uchun) | |
| `Procfile` | Railway serverni qanday ishga tushirishi | |
| `.env.example` | Maxfiy sozlamalar namunasi (HF_TOKEN, ADMIN_KEY ...) | "Parollar kodda emas" |

## Frontend (`frontend/`) — sayt, HTML + CSS + JavaScript
| Fayl | Nima haqida |
|---|---|
| `index.html` | Asosiy sahifa: qidiruv, xonalar, bino va qavatlar, kutib olish xizmati, galereya, balkondan ko'rinish, xodimlar, joylashuv (xarita), hujjatlar, bronlarim, chat |
| `app.js` | Saytning barcha mantig'i (9 bo'lim, fayl boshida ro'yxati bor) |
| `style.css` | Barcha ko'rinish (ranglar, kartalar, mobil moslashuv, qulaylik) |
| `admin.html` | Admin panel |
| `config.js` | Backend manzili (deploydan keyin shu yer o'zgaradi) |
| `netlify.toml` | Netlify sozlamasi: kesh va xavfsizlik sarlavhalari |
| `img/*.jpg`, `img/CREDITS.md` | Haqiqiy namunaviy suratlar (nomi bo'yicha guruhlangan: `exterior-*` bino, `lobby-*`, `welcome-*` kutib olish, `bath-*` hammom, `corridor-*` yo'lak, `kitchen-*`, `restaurant-*`, `hall-*` zal, `garden-*`/`park-*` yashil hudud, `room-*`/`bed-*`/`suite-*` yotoqxona, `balcony-view.jpg` balkondan ko'rinish) va mualliflar ro'yxati |
| `tests/smoke.js` | Sayt testi (44 tekshiruv) |

## Boshqalar
| Fayl | Nima haqida |
|---|---|
| `main.py` | PyCharm'da yashil ▶ bilan hammasini ishga tushiradi: kutubxonalarni o'rnatadi, backend + saytni yoqadi, brauzerni ochadi |
| `ishga_tushir.bat` | Windows'da bir bosish bilan ishga tushirish (kutubxona + 2 server + brauzer) |
| `docs/01-talablar.md` | Talablar (SRS), jarayon modeli, xavflar |
| `docs/02-loyihalash.md` | Arxitektura, use-case, ER va ketma-ketlik diagrammalari |
| `docs/03-test-hisoboti.md` | Test natijalari va topilgan xatolar |
| `docs/04-samaradorlik-hisoboti.md` | Tezlik o'lchovlari: oldin va keyin |
| `docs/05-mehmonxona-standartlari.md` | Xona turlari, bino, standartlar, hujjatlar, xodimlar |
| `docs/06-fayllar-xaritasi.md` | Shu fayl |
| `README.md` | Ishga tushirish, deploy, himoya savollari |
| `.gitignore` | GitHub'ga yuklanmaydigan fayllar (`.env`, `hotel.db`) |

## Ma'lumot qayerdan qayerga oqadi?
```
hotel_info.py + seed.py ──► baza (hotel.db) ──► main.py (API) ──► app.js ──► index.html (ko'rinish)
                                    ▲                │
                          services.py (qoidalar)     └──► ai.py (Hugging Face / zaxira)
```
