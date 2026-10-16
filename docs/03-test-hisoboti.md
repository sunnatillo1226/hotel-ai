# 3. Test hisoboti

## 3.1. Test turlari
| Tur | Nima tekshiriladi | Qanday |
|---|---|---|
| Birlik / API testlari | Backend qoidalari va API javoblari | `pytest` — `backend/tests/test_api.py` |
| Integratsion (sayt + backend) | Sayt kodi haqiqiy backend bilan birga ishlaydi: qidiruv, bron, sharh, chat | jsdom bilan avtomatik skript, `frontend/tests/smoke.js` (44 tekshiruv) |
| Tezlik testi | Javob vaqti va hajmi | `backend/benchmark.py` |
| Qo'lda tekshiruv | Ko'rinish, telefon, fokus | Brauzerda ko'rish (quyida jadval) |

## 3.2. Natija
| Test to'plami | Soni | O'tdi | O'tmadi |
|---|---|---|---|
| `pytest` (backend) | 42 | 42 | 0 |
| Sayt + backend integratsion skript | 44 | 44 | 0 |

Ishga tushirish:
- Backend testlari: `cd backend && pip install -r requirements-dev.txt && pytest -v`
- Sayt testi (backend ishlab turishi kerak): `cd frontend/tests && npm install jsdom && node smoke.js`

## 3.3. Talablar va testlar bog'liqligi
| Talab | Tekshiruvchi test |
|---|---|
| FR-01 | `test_rooms_list_sorted_by_price`, `test_rooms_have_rating_from_seed_reviews` |
| FR-02 | `test_rooms_filter_by_guests`, `test_availability_flag_updates` |
| FR-03 | `test_ai_recommend_family_first`, `test_ai_keyword_not_matched_inside_word`, `test_ai_recommend_skips_fully_booked_type` |
| FR-04 | `test_booking_success_and_price` |
| FR-05 | `test_quantity_limits_overlapping_bookings`, `test_back_to_back_booking_allowed`, `test_remaining_and_availability_flag` |
| FR-12 | `test_hotel_profile`, `test_suited_for_filter`, `test_ai_detects_audience`, `test_ai_chat_documents_and_parking`, `test_chat_*` (suhbat sifati: til, kontekst, tavsiya, maxfiylik) + saytdagi "Kimlar uchun", hujjatlar, joylashuv tekshiruvlari |
| FR-06 | `test_booking_validation` (o'tgan sana, 0 kecha, sig'im, 30 kecha, 1 yil, email) |
| FR-07 | `test_my_bookings_email_is_case_insensitive`, `test_cancel_frees_room_and_checks_owner` |
| FR-08 | `test_review_sentiment`, `test_review_validation` |
| FR-09 | `test_ai_chat_fallback` |
| FR-10 | `test_admin_requires_key`, `test_admin_stats_numbers` |
| FR-11 | `test_ai_chat_fallback`, `test_review_sentiment` (token yo'q holatda ishlaydi) |
| FR-13 | `test_booking_requires_identity_document`, `test_couple_needs_marriage_certificate` + saytda guvohnoma maydoni tekshiruvi |
| FR-14 | `test_floors_are_separated_by_guest_type`, `test_rooms_have_multiple_photos`, `test_hotel_gallery_welcome_and_balcony`, `test_distances_computed_from_coordinates`, `test_chat_family_floor_and_location` |
| NFR-02 | `test_response_time_header_and_gzip` |

## 3.4. Test va kod ko'rib chiqish paytida topilgan, tuzatilgan xatolar
| # | Xato | Sabab | Tuzatish |
|---|---|---|---|
| 1 | "100$ **gacha** xona" so'rovida "konditsioner" qulayligi noto'g'ri tanlanardi | Kalit so'z `ac` so'zning o'rtasidan ham mos kelardi ("g**ac**ha") | Kalit so'z faqat so'z boshidan mos keladigan qilindi; himoya uchun `test_ai_keyword_not_matched_inside_word` yozildi |
| 2 | "Chiqish vaqti" savoliga salom bilan javob berilishi mumkin edi (kod ko'rib chiqishda topildi) | `hi` kalit so'zi "c**hi**qish" ichidan topilardi | Xuddi shu tuzatish; `test_ai_chat_fallback` shuni tekshiradi |
| 3 | Bron qilingach xonalar ro'yxati o'zi qayta yuklanib, AI natijalari yo'qolardi | Bron/bekor qilishdan keyin avtomatik yangilash | Avtomatik yangilash olib tashlandi |
| 4 | Ro'yxat sekin ishlardi (150 xonada 168 ms) | Har xona uchun alohida so'rov (N+1) | Bitta so'rovga birlashtirildi — 4-hisobotga qarang |
| 5 | Eski model: har xona turi faqat bitta bron qabul qilardi (real mehmonxonada bir turdan o'nlab xona bor) | Xona turi va xona soni ajratilmagan edi | `quantity` maydoni va `peak_occupancy` — har kecha band xonalar soni sig'imdan oshmasin |
| 6 | Eski `hotel.db` yangi ustunlarsiz qolsa, server tushunarsiz xato berardi | Jadval avtomatik o'zgarmaydi | Ishga tushishda tekshiruv va aniq xabar: `hotel.db` ni o'chiring |

## 3.5. Qo'lda tekshiruv ro'yxati (himoya oldidan ko'rib chiqing)
| Tekshiruv | Natija |
|---|---|
| Telefon o'lchamida (brauzerda F12 → telefon ko'rinishi) sayt to'g'ri ko'rinadi | ☐ |
| Tab tugmasi bilan hamma tugmaga o'tish mumkin, fokus ramkasi ko'rinadi | ☐ |
| Esc tugmasi chatni yopadi | ☐ |
| Bepul server uyg'onayotganda "Server uyg'onmoqda" xabari chiqadi | ☐ |
| HF tokeni qo'yilganda sayt pastida "AI faol" yozuvi chiqadi | ☐ |

## 3.6. Hali sinalmagan narsalar (halol aytiladi)
- Ko'rinish haqiqiy Chromium'da skrinshot bilan ko'rib chiqildi (kompyuter va telefon kengligi): rasmlar yuklanadi, gorizontal aylanish yo'q. Safari/Firefox va haqiqiy telefonda sinalmagan.
- Haqiqiy Hugging Face modeli (token kerak) — testlar zaxira rejimda o'tgan.
- Avtomatik sayt testi jsdom (brauzer simulyatori) bilan; to'liq ko'rinishni o'zingiz ham ko'rib chiqing.
- Railway va Netlify'da jonli joylashtirish (3-iteratsiya).
