# 1. Talablar spetsifikatsiyasi (SRS)

**Loyiha:** Silk Road Grand Hotel — AI bilan xona bron qilish tizimi
**Fan:** Dasturiy injiniringga kirish

## 1.1. Maqsad
Mehmonlar mehmonxona xonalarini onlayn, tez va qulay bron qilishi uchun veb-tizim yaratish. Sun'iy intellekt qidiruvni osonlashtiradi, savollarga javob beradi va sharhlarni tahlil qiladi.

## 1.2. Muammo va yechim
| Muammo (real hayotda) | Tizimdagi yechim |
|---|---|
| Mehmon telefon qilib xona so'rashi kerak, vaqt ketadi | Onlayn qidiruv va bron, 24/7 |
| Bir xonaga ikki kishi bron qilib qo'yishi mumkin | Sanalar kesishuvini avtomatik tekshirish |
| Mehmon ko'p filtrni qo'lda tanlashi kerak | AI qidiruv: "4 kishi, balkonli, 160$ gacha" deb yozsa yetadi |
| Admin yuzlab sharhni o'qib chiqolmaydi | AI har sharhning kayfiyatini aniqlaydi, statistika chiqadi |
| Bir xil savollarga xodim qayta-qayta javob beradi | AI chat yordamchi |

## 1.3. Foydalanuvchilar (aktorlar)
- **Mehmon** — xona qidiradi, bron qiladi, bekor qiladi, sharh yozadi, chatdan foydalanadi.
- **Admin** — statistika va barcha bronlarni ko'radi.
- **Tashqi tizim: Hugging Face** — AI javoblarini beradi.

## 1.4. Funksional talablar
| Kod | Talab |
|---|---|
| FR-01 | Tizim barcha xonalarni narx, sig'im, qulayliklar va reyting bilan ko'rsatadi |
| FR-02 | Mehmon sana, mehmonlar soni va xona turi bo'yicha qidira oladi; har xona "Bo'sh/Band" deb belgilanadi |
| FR-03 | Mehmon erkin matn bilan (AI qidiruv) xona qidira oladi; tizim nimani tushunganini ko'rsatadi |
| FR-04 | Mehmon xonani bron qila oladi; jami narx avtomatik hisoblanadi va bron kodi beriladi |
| FR-05 | Shu turdagi barcha xonalar band bo'lsa bron qilib bo'lmaydi (har tur uchun `quantity` ta xona bor); bir mehmon chiqqan kuni ikkinchisi kirishi mumkin |
| FR-06 | Bron qoidalari: o'tgan sana mumkin emas; eng ko'pi 30 kecha; eng ko'pi 1 yil oldin; mehmonlar soni xona sig'imidan oshmasin |
| FR-07 | Mehmon email orqali o'z bronlarini ko'ra oladi va bekor qila oladi (faqat egasi) |
| FR-08 | Mehmon sharh va baho (1–5) qoldira oladi; AI sharh kayfiyatini (ijobiy/neytral/salbiy) aniqlaydi |
| FR-09 | AI chat yordamchi mehmonxona va xonalar haqidagi savollarga javob beradi |
| FR-10 | Admin kalit bilan kirib, statistika (bronlar, tushum, bandlik %, kayfiyat) va bronlar ro'yxatini ko'radi |
| FR-12 | Sayt mehmonxona haqida to'liq ma'lumot beradi: xona turlari va kimlar uchun ekani, bino va joylashuv, qulayliklar, avtoturargoh, bron uchun hujjatlar (`GET /api/hotel`). Batafsil: `05-mehmonxona-standartlari.md` |
| FR-13 | Bron uchun shaxsni tasdiqlovchi hujjat (pasport / ID-karta / xalqaro pasport) turi va raqami majburiy; er-xotin sifatida joylashganlardan nikoh guvohnomasi raqami ham majburiy (kamida 2 mehmon). Hujjat raqami API da faqat niqoblangan (`••••567`) qaytadi |
| FR-14 | Qavatlar toifalar bo'yicha ajratilgan (oilalar — 3-qavat, yakka mehmonlar — 4, juftliklar — 5–6, Twin — 7, Deluxe — 8, Suite — 9, moslashgan xonalar — 2); har xona turida kamida 3 ta surat; balkondan ko'rinish, kutib olish xizmati va xarita ko'rsatiladi |
| FR-11 | AI xizmati ishlamasa, tizim to'xtamasdan zaxira rejimda ishlashda davom etadi |

## 1.5. Nofunksional talablar
| Kod | Turi | Talab | Qanday tekshiriladi |
|---|---|---|---|
| NFR-01 | Tezlik | Xonalar ro'yxati serverda 100 ms dan tez (150 xonada ham) | `benchmark.py` |
| NFR-02 | Tezlik | Ro'yxat javobi tarmoqda 5 KB atrofida (gzip) | `benchmark.py` |
| NFR-03 | Tezlik | Ma'lumot kelguncha foydalanuvchi bo'sh ekran emas, yuklanish holatini ko'radi | Qo'lda ko'rish |
| NFR-04 | Qulaylik | Telefonda ham ishlaydi (moslashuvchan dizayn) | Qo'lda ko'rish |
| NFR-05 | Qulaylik | Klaviaturadan foydalanish mumkin (Tab, Esc), aniq fokus ramkasi, o'qiladigan kontrast | Kod tekshiruvi |
| NFR-06 | Qulaylik | Xato xabarlari tushunarli o'zbek tilida ("Bu xona tanlangan sanalarda band") | `test_api.py` |
| NFR-07 | Ishonchlilik | AI uzilsa ham sayt ishlaydi; AI javobi kutish chegarasi: chat 20 s, qolgani 8 s | `test_api.py` (zaxira testlari) |
| NFR-08 | Xavfsizlik | Kiruvchi ma'lumot tekshiriladi; SQL injection va XSS dan himoya; sirlar kodda emas, `.env` da | Kod tekshiruvi |
| NFR-09 | Kengayuvchanlik | Baza almashtirilishi mumkin (SQLite → PostgreSQL) kodni o'zgartirmasdan | `database.py` |

## 1.6. Cheklovlar va taxminlar
- To'lov tizimi va email orqali tasdiqlash hozircha yo'q.
- Admin himoyasi oddiy kalit asosida (keyingi versiyada JWT login).
- Narxlar dollarda ko'rsatiladi (oddiylik uchun).
- Bepul hostingda (Railway) server uzoq vaqt ishlatilmasa uxlab qolishi mumkin; sayt bunda "Server uyg'onmoqda" xabarini ko'rsatadi.

## 1.7. Ishlab chiqish jarayoni modeli
**Iterativ (Agile'ga yaqin) model** tanlandi: loyiha 4 ta qisqa iteratsiyaga bo'lindi, har birining oxirida ishlaydigan natija va test bor.

| Iteratsiya | Natija |
|---|---|
| 1 | Baza, API, qoidalar |
| 2 | Sayt, admin panel, AI ulash, lokal sinov |
| 3 | Tezlik va qulaylikni yaxshilash, testlar, hujjatlar |
| 4 | Deploy (Railway + Netlify), jonli sinov, himoyaga tayyorgarlik |

**Asosiy xavflar:**
| Xavf | Ehtimol | Chora |
|---|---|---|
| AI xizmati ishlamasligi yoki sekin javob berishi | O'rta | Zaxira rejim + kutish chegarasi |
| Ikki mehmon bir xonani bron qilishi | Past | Server tomonida kesishuvni tekshirish + test |
| Bepul server uxlab qolishi | O'rta | Foydalanuvchiga xabar ko'rsatish |
| Token/parol GitHub'ga chiqib ketishi | O'rta | `.env` `.gitignore` da, `.env.example` namuna |
