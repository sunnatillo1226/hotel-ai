# 4. Samaradorlik (tezlik) hisoboti

## 4.1. Qanday o'lchandi
- Skript: `backend/benchmark.py` (ishga tushirish: `python benchmark.py`).
- Sinov hajmi real mehmonxonaga yaqin: **150 xona, 3000 bron, 1500 sharh**.
- Har bir so'rov **30 marta** chaqirildi; **o'rtacha** (median) va **p95** (30 so'rovdan 95% i shu vaqtdan tez) hisoblandi.
- Baza: SQLite (vaqtinchalik fayl). Asl bazaga tegilmaydi.

## 4.2. Natija: oldin va keyin
| So'rov | Oldin (o'rtacha) | Keyin (o'rtacha) | Tezlashish | p95 oldin → keyin |
|---|---|---|---|---|
| Xonalar ro'yxati (sanasiz) | 57.9 ms | 9.1 ms | **6.4 marta** | 84.1 → 12.9 ms |
| Xonalar ro'yxati (sana bilan, band tekshiruvi) | 167.7 ms | 10.0 ms | **16.8 marta** | 237.2 → 12.6 ms |
| AI qidiruv (`/api/ai/recommend`) | 125.5 ms | 7.9 ms | **15.9 marta** | 145.0 → 9.9 ms |
| Admin: barcha bronlar | 30.3 ms | 17.7 ms | 1.7 marta | 43.4 → 25.1 ms |
| Admin: statistika | 8.8 ms | 12.2 ms | o'zgarmadi* | 12.2 → 15.4 ms |

\* Statistika so'rovi o'zgartirilmagan; farq o'lchash shovqini doirasida (bir necha millisekund).

**Tarmoqdan o'tadigan ma'lumot hajmi (gzip siqishdan keyin):**
| So'rov | Oldin | Keyin | Kamayish |
|---|---|---|---|
| Xonalar ro'yxati (150 xona) | 34.5 KB | 2.2 KB | **15.7 marta** |
| Admin: bronlar | 51.5 KB | 4.2 KB | 12.3 marta |

## 4.3. Nima o'zgartirildi va nima uchun
| O'zgarish | Nima beradi |
|---|---|
| **N+1 muammosini bartaraf etish.** Oldin har bir xona uchun 2 ta alohida so'rov ketardi (150 xonada ~300 ta so'rov). Endi hammasi 2 ta so'rovda (`rating_stats`, `peak_occupancy` — `services.py`) | Eng katta tezlanish; xona soni oshganda ham sekinlashmaydi |
| **Bazada indekslar** (`bookings(room_id, check_in, check_out)`, `bookings(guest_email)`, `reviews(room_id)`) | Bandlikni tekshirish va email bo'yicha qidirish tez |
| **`joinedload`** — bronlar ro'yxatida xona nomini bitta so'rovda olish | Admin ro'yxati tezlashdi |
| **GZip siqish** (`GZipMiddleware`) | Javob hajmi ~15 marta kichik => sekin internetda sayt tez ochiladi |
| **AI kutish chegarasi** (chat 20 s, qolganlari 8 s, ulanish 4 s) | AI sekin bo'lsa, mehmon uzoq kutmasdan zaxira javob oladi |
| **Skelet kartalar** (yuklanish holati), `defer` skriptlar, favicon so'rovi yo'q | Foydalanuvchi uchun sayt tezroq "his qilinadi" |
| **Brauzer keshi** (Netlify sarlavhalari: CSS/JS 1 soat) | Qayta kirganda sayt deyarli darrov ochiladi |
| **`X-Process-Time` sarlavhasi** | Har bir javobning server vaqtini brauzerda (F12 → Network) ko'rish mumkin |

## 4.4. Talablar bilan solishtirish
| Talab | Maqsad | Natija |
|---|---|---|
| NFR-01 | Ro'yxat serverda < 100 ms (150 xonada) | ✅ 10 ms |
| NFR-02 | Ro'yxat javobi tarmoqda ~5 KB | ✅ 2.2 KB |

## 4.4.1. Xona turlari (quantity) modeliga o'tgandan keyingi qayta o'lchov
Har bir `Room` qatori endi xona *turi* (`quantity` ta xona). Band-bo'shlikni hisoblash ham bitta so'rovda (`peak_occupancy`: har kecha uchun band xonalar soni). Natija o'zgarmadi (150 turli sinov bazasi, 3000 bron):

| So'rov | O'rtacha | p95 | Tarmoqda (gzip) |
|---|---|---|---|
| Xonalar (sanasiz) | 8.6 ms | 10.3 ms | 2.3 KB |
| Xonalar (sana bilan) | 10.1 ms | 15.5 ms | 2.4 KB |
| AI qidiruv | 8.0 ms | 11.3 ms | 0.4 KB |
| Admin: statistika | 12.3 ms | 13.4 ms | 0.8 KB |
| Admin: bronlar | 19.4 ms | 24.7 ms | 4.1 KB |

Xom javob hajmi yangi maydonlar (m², karavot turi, kimlar uchun) tufayli 34 → 50 KB bo'ldi, lekin gzip'dan keyin farq deyarli yo'q.

## 4.5. Cheklovlar (halol aytiladi)
- O'lchov **tarmoqsiz**, server ichida bajarildi. Haqiqiy foydalanuvchida internet tezligi, Railway serverining joylashuvi va (bepul tarifda) serverning "uyg'onish" vaqti qo'shiladi. Shuning uchun bu raqamlar **server ishining tezligini** ko'rsatadi, mehmon ko'radigan to'liq vaqtni emas.
- **AI javob vaqti** (Hugging Face) bu o'lchovga kirmagan: u tashqi xizmatga bog'liq, odatda soniyalar. Shu sababli kutish chegarasi va zaxira rejim qo'yilgan.
- Brauzerdagi to'liq yuklanish (Lighthouse) o'lchanmagan. Deploydan keyin Chrome'da F12 → Lighthouse orqali o'lchab, natijani shu hisobotga qo'shish tavsiya etiladi.
- Mavjud bazalarga indekslar avtomatik qo'shilmaydi (faqat yangi jadvalga). Railway'da yangi PostgreSQL ochilgani uchun bu muammo emas.

## 4.6. Keyingi yaxshilash imkoniyatlari
Natijalarni xotirada qisqa muddat saqlash (kesh), xona rasmlarini WebP formatiga o'tkazish (hozir rasmlar 800 px JPEG, `loading=lazy` bilan yuklanadi), PostgreSQL'da ulanishlar havzasi (connection pool).
