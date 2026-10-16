# 5. Mehmonxona: xona turlari, bino, standartlar va hujjatlar

> **Muhim (halol aytiladi):** Silk Road Grand Hotel — *o'quv (namunaviy)* mehmonxona. Manzil, narx va miqdorlar loyiha parametrlari.
> Mehmonxona jahon mezonlariga **moslab loyihalangan**, lekin **rasmiy sertifikatlanmagan** (haqiqiy sertifikatni faqat vakolatli tashkilot beradi).
> Barcha ma'lumot bir joyda turadi: `backend/hotel_info.py` va `backend/seed.py`; sayt va AI shundan oladi.

## 5.1. Umumiy ko'rinish
| Ko'rsatkich | Qiymat |
|---|---|
| Toifa | 4 yulduzli shahar mehmonxonasi (biznes + oilaviy dam olish) |
| Joylashuvi | Toshkent, Mirobod tumani, Amir Temur xiyoboni yaqinida (namunaviy manzil) |
| Bino | 9 ta yer usti qavat + 2 ta yer osti avtoturargoh qavati, 3 ta lift |
| Xonalar | 84 ta, 8 xil turda (2–9-qavatlarda, **qavatlar toifalar bo'yicha ajratilgan**) |
| Xizmat | 24 soat resepshn; o'zbek, rus, ingliz tillari |
| Check-in / out | 14:00 dan / 12:00 gacha |

### Bino tuzilishi
| Qavat | Nima joylashgan |
|---|---|
| −2, −1 | Yopiq avtoturargoh (60 o'rin, 5 ta elektromobil quvvatlash) |
| 1 | Lobby, 24 soatlik resepshn, restoran va bar, konferensiya zali (80 kishi), yuk saqlash |
| 2 | Moslashgan xonalar (ACC, 6 ta, liftga eng yaqin), fitnes zal, sauna |
| 3 | **Oilaviy qavat:** faqat Family xonalar (8 ta) — oilalar alohida, tinch qavatda |
| 4 | Yakka mehmonlar: Single (12 ta) |
| 5–6 | Juftliklar: Double (20 ta, har qavatda 10 tadan) |
| 7 | Do'stlar/hamkasblar: Twin (16 ta) |
| 8 | Balkonli Deluxe (14 ta) |
| 9 | Suite qavati: Junior Suite (6 ta) va Prezident Suite (2 ta) |

Nega qavatlar ajratilgan? Real mehmonxonalarda oilalar (bolalar shovqini), yakka mehmonlar va VIP mehmonlar alohida qavatlarga joylanadi — bir-biriga xalaqit bermasligi uchun; nogironlar uchun xonalar lift yaqinida past qavatda bo'ladi.

### Kirish, favvora va xodimlar
- **Favvora:** bosh kirish oldida favvorali yashil maydon; kechqurun yoritiladi.
- **Soyabonli kirish:** avtomatik shisha eshiklar, eshik oldi xizmatchisi (yomg'irda soyabon tutadi, taksi chaqiradi).
- **Valet:** mashinani kirish oldida qoldirasiz → formadagi xodim yer osti avtoturargohga olib boradi → so'raganingizda 3–5 daqiqada eshik oldiga olib keladi. Mehmonlar uchun bepul, raqamli kvitansiya beriladi.
- **Forma:** barcha xodim ismi yozilgan nishon bilan. Eshik oldi xizmatchisi va yuk tashuvchilar (bellboy) — qizil (bordo) forma, oq qo'lqop, qora bosh kiyim (suratlardagidek); valet — yashil kurtka, oltin tugma, kepka; resepshn — qora kostyum; xona xizmati — och forma va oq fartuk; xavfsizlik — qora forma. To'liq ro'yxat saytda "Xodimlar va xizmat" bo'limida.
- **Bino:** saytda haqiqiy namunaviy surat va yonida qavatlar ro'yxati; qavatni bossangiz, u yerdagi xonalar va xizmatlar chiqadi. Oldin chizilgan multfilm uslubidagi rasm olib tashlandi (real ko'rinish uchun).

### Joylashuv (nega shu joy?)
Shahar markazi, metroga ~500 m, aeroportga ~4–5 km (mashinada 15–20 daqiqa), xiyobonga ~300 m. Biznes mehmon ham, sayyoh ham, oila ham qulay. Aeroport masofasi ochiq manbadan olingan; qolgan masofalar namunaviy.

## 5.2. Xona turlari va ular kimlar uchun
Xona kodlari (SGL, DBL, TWN ...) mehmonxona sohasida keng qo'llaniladigan qisqartmalar.

| Kod | Xona turi | Narx/kecha | Sig'im | Soni | Maydon | Karavot | Kimlar uchun |
|---|---|---|---|---|---|---|---|
| SGL | Standart Single | 55$ | 1 | 12 | 18 m² | 1 yakka (1,20 m) | yolg'iz sayohatchi, xizmat safari |
| DBL | Standart Double | 70$ | 2 | 20 | 22 m² | 1 ikki kishilik (1,60 m) | **er-xotin va juftliklar**, yolg'iz |
| TWN | Standart Twin | 72$ | 2 | 16 | 22 m² | 2 yakka (0,90 m) | do'stlar, hamkasblar |
| ACC | Moslashgan (Accessible) | 70$ | 2 | 6 | 26 m² | 1 ikki kishilik, past | **nogironligi bo'lgan mehmonlar** |
| DLX | Deluxe Double, balkonli | 95$ | 3 | 14 | 28 m² | king-size (1,80 m) | juftliklar, dam olish, biznes |
| FAM | Family xona | 130$ | 4 | 8 | 36 m² | 1 ikki kishilik + 2 yakka | **oilalar (bolalar bilan)** |
| JSU | Junior Suite | 150$ | 3 | 6 | 42 m² | king-size + divan-karavot | asal oyi, yubiley, uzoq safar |
| PRS | Prezident Suite | 320$ | 4 | 2 | 95 m² | 2 yotoqxona, 2 king-size | VIP, yubiley, delegatsiya |

**Nima uchun aynan shunday?** Haqiqiy mehmonxonada eng ko'p xona — standart turlar (SGL/DBL/TWN, jami 48 ta), premium turlar kam (PRS atigi 2 ta). Shu sababli narx va soni piramida shaklida. Narxlar ham raqobatchilar mantig'iga mos: oddiy xonadan suitegacha ~6 barobar farq.

**Bizning g'oyalarimiz** (oddiy saytlarda yo'q):
1. **"Kimlar uchun?" filtri** — mehmon xona nomini bilmasa ham o'ziga mosini topadi (er-xotin, oila, do'stlar, biznes, VIP, nogironlar).
2. **AI kimligini tushunadi:** "turmush o'rtog'im bilan asal oyiga" → `audience = couple`, mos xonalar yuqoriga chiqadi.
3. **"Qolgan: N xona"** — tanlangan sanalarda shu turdan nechta qolganini ko'rsatadi (real tizimlardagi kabi).
4. **Hujjatlar bo'limi** — mehmon kelishdan oldin nima olib kelishni biladi, resepshnda ortiqcha talab bo'lmaydi.
5. Moslashgan xonalar alohida tur sifatida (ko'p saytlarda yo'q).

## 5.3. Bron qilishda qanday hujjatlar kerak?
Bron formasida **hujjat turi (pasport / ID-karta / xalqaro pasport) va raqami majburiy** (rasmini yuklash shart emas). Asl hujjat joylashishda (check-in) resepshnda ko'rsatiladi. Raqam bazada saqlanadi, lekin API faqat oxirgi 3 raqamini qaytaradi (`••••567`) — maxfiylik uchun.

| Mehmon | Nima kerak |
|---|---|
| O'zbekiston fuqarosi | Pasport yoki ID-karta (har bir kattalar mehmon uchun). Yangi namunadagi haydovchilik guvohnomasi ham shaxsni tasdiqlovchi hujjat |
| Chet el fuqarosi | Xalqaro pasport (kerak bo'lsa viza). Mehmonxona uni elektron tizimda ro'yxatga oladi |
| **Er-xotin / juftlik** | Har birining shaxsiy hujjati + **nikoh guvohnomasi** (bron formasida "Biz er-xotinmiz" belgisi → guvohnoma raqami majburiy, kamida 2 mehmon). Do'stlar, hamkasblar va qarindoshlardan guvohnoma so'ralmaydi |
| **Oila (bolalar bilan)** | Ota-ona juftlik sifatida joylashsa — nikoh guvohnomasi; propiska so'ralmaydi. Bolalar ro'yxatiga tug'ilganlik guvohnomasi yoki ID ma'lumoti olinadi (ichki qoida). 18 yoshgacha kattalarsiz joylashtirilmaydi (ichki qoida) |

⚠️ **Ishonchlilik darajasi:** bu mehmonxonaning **ichki qoidasi** (ustoz talabi bo'yicha: bron uchun shaxsni tasdiqlovchi hujjat va er-xotinlar uchun guvohnoma). 2023-yil fevralidagi ommaviy xabarlarda O'zbekistonda mehmonxonalar nikoh guvohnomasi/propiska talab qilishi taqiqlangani aytilgan edi — buni rasmiy matndan tasdiqlay olmadim. Chet elliklarni ro'yxatga olish tartibi o'zgarib turadi. **Himoyadan oldin lex.uz saytida tekshirib qo'ying** va "qoidalar o'zgarishi mumkin" deb ayting. Bolalar va 18 yoshgacha bo'lgan qoidalar — namunaviy mehmonxonaning ichki qoidasi, qonun emas.

## 5.4. Qulayliklar va avtoturargoh
- **Avtoturargoh:** yopiq yer osti, 60 o'rin, mehmonlar uchun **bepul**; 5 ta elektromobil quvvatlash joyi; 4 ta kengaytirilgan o'rin (nogironlar); valet va video-kuzatuv; balandlik chegarasi 2,1 m; avtobus tushirish joyi, velosiped saqlash.
- **Ovqatlanish:** shved stoli nonushta (07:00–10:30, narxga kiritilgan), restoran, lobby-bar, xonaga ovqat (07:00–23:00), bolalar menyusi.
- **Xonada:** tezkor Wi-Fi, konditsioner, TV, elektron kalit, fen, choynak, seyf; yuqori toifalarda xalat, kofe mashina, minibar, balkon; PRS'da jakuzi.
- **Oilalar:** bolalar beshigi bepul, 6 yoshgacha bolalar bepul, qo'shimcha karavot 15$, ulanadigan xonalar (so'rov bilan).
- **Biznes:** 80 kishilik konferensiya zali, biznes burchak, ish stoli.
- **Xavfsizlik va qulaylik:** yong'in signalizatsiyasi, evakuatsiya rejalari, video-kuzatuv, barcha qavatlarga lift, 6 ta moslashgan xona.
- **Bepul xizmatlar (qonun talabi):** tez yordam chaqirish, dori qutisi, qaynatilgan suv, ip-igna, idish-tovoq to'plami.

## 5.5. Standartlarga mosligi (mezonma-mezon)
Quyida ishlatilgan asosiy manbalar: **Hotelstars Union** (Yevropa va ko'p davlatlarda ishlatiladigan 1–5 yulduzli tizim), **O'z DSt 3296:2018** (O'zbekistonning mehmonxona xizmatlari bo'yicha davlat standarti) va **UNWTO** tasnifi. Quyidagi jadval mezonlarning umumiy mohiyatini aks ettiradi; aniq raqamlarni rasmiy hujjatdan tekshiring.

| Mezon (4 yulduz uchun odatiy) | Bizda | Holat |
|---|---|---|
| 24 soat ishlaydigan resepshn, xodim doim mavjud | Bor | ✅ moslab loyihalangan |
| Kamida bir necha tilda xizmat | o'zbek, rus, ingliz | ✅ |
| Shaxsiy hammom har xonada, konditsioner, TV | Barcha xonalarda | ✅ |
| Bepul Wi-Fi | Bor | ✅ |
| Nonushta | Shved stoli, narxga kiritilgan | ✅ |
| Yuk tashish / saqlash xizmati, lift | Bor, 3 ta lift | ✅ |
| Kir yuvish, dazmollash | Bor | ✅ |
| Xonalarni kundalik tozalash | Qabul qilingan (xizmat qoidasi) | ✅ |
| Nogironlar uchun moslashgan xonalar va kirish | 6 ta xona, 4 ta o'rin | ✅ |
| Yong'in xavfsizligi, evakuatsiya | Bor | ✅ (loyihada; real tekshiruv kerak) |
| Fitnes zal / sauna / konferensiya (qo'shimcha ball) | Bor | ✅ |
| Rasmiy yulduz toifasi (sertifikat) | **Yo'q** — rasmiy baholash o'tmagan | ❌ halol: sertifikatlanmagan |
| Real bino, litsenziya, soliq ro'yxati | **Yo'q** — o'quv loyiha | ❌ |

**Xulosa:** mehmonxona 4 yulduzli toifa *g'oyasi va xizmatlar to'plami* jihatidan jahon mezonlariga mos loyihalangan; ammo bu rasmiy sertifikat emas. Ustozga "jahon standartlariga mos keladimi?" degan savolga: **"mezonlarga moslab loyihaladik, rasmiy sertifikat esa real bino qurilgandan keyin olinadi"** deb javob bering.

## 5.6. Rasmlar haqida
Rasmlar Pexels (bepul litsenziya) va Pixabay saytlaridan, ustoz ruxsati bilan olingan; yana 3 ta rasmni (lobby ×2, hovuzli bino) foydalanuvchi namuna sifatida taqdim etgan (manba/litsenziyasini alohida tekshirish kerak). Ular **namunaviy (illyustrativ)** — bu aynan shu mehmonxona emas. Har bir xona turida 3–5 ta surat (yotoqxona, dush/hammom, balkon, yo'lak), mehmonxona bo'yicha esa kutib olish, lobby, yo'lak, restoran, oshxona, zal, yashil hudud va xiyobon suratlari bor. **Balkondan ko'rinish** — kollaj: haqiqiy Toshkent teleminorasi (Pixabay, xusenru) va xiyobon (Pexels) suratlari birlashtirilgan; saytda buning izohi yozilgan. Ro'yxat: `frontend/img/CREDITS.md`. Bir nechta surat bir necha xonada takrorlanadi (zaxira yetarli emas).

## 5.7. Himoya uchun: tez-tez beriladigan savollar
- **Nima uchun xona turi va xona soni alohida ajratilgan?** Haqiqiy mehmonxonada bir turdan ko'p xona bor; `Room` — tur, `quantity` — soni. Bo'sh-band tekshiruvi eng band kechada `quantity − band` ni hisoblaydi (`services.peak_occupancy`).
- **Mehmonxona ma'lumoti qayerda?** `hotel_info.py` — yagona manba; sayt `GET /api/hotel` orqali oladi, AI chat ham shu matndan javob beradi (o'zidan to'qimaydi).
- **Nima uchun er-xotinlardan nikoh guvohnomasi so'raladi?** Bu loyiha talabi va mehmonxonaning ichki qoidasi. Haqiqatda bunday talab qonuniy ekanini lex.uz da tekshirish kerak (5.3-bo'limdagi ogohlantirish). Kod shu qoidani `schemas.BookingCreate` validatorida tekshiradi; qoida o'zgarsa, bitta joyni o'zgartirish yetadi.
- **Nima uchun qavatlar ajratilgan?** "Bino tuzilishi" jadvali: oilalar 3-qavatda, yakka mehmonlar 4-da va h.k. `seed.py` dagi `floors` maydoni shuni belgilaydi; sayt va AI shu ma'lumotdan foydalanadi.
