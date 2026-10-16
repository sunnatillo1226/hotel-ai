# 2. Loyihalash (arxitektura va diagrammalar)

Diagrammalar **Mermaid** formatida. GitHub'da avtomatik chizma bo'lib ko'rinadi; PyCharm'da Mermaid plagini yoki https://mermaid.live saytida ochish mumkin.

## 2.1. Umumiy arxitektura (3 qatlamli)

```mermaid
flowchart LR
    U[Mehmon / Admin<br/>brauzer] -->|HTTPS, JSON| F[Frontend<br/>HTML + CSS + JS<br/>Netlify]
    F -->|fetch /api/...| B[Backend<br/>Python FastAPI<br/>Railway]
    B -->|SQLAlchemy| D[(Baza<br/>PostgreSQL / SQLite)]
    B -->|HTTPS| H[Hugging Face<br/>AI modeli]
    H -.->|xato yoki sekin bo'lsa| Z[Zaxira rejim<br/>qoidalar asosida]
    B --- Z
```

**Qatlamlar:**
1. **Taqdimot qatlami** — `frontend/` (ko'rinish va foydalanuvchi bilan muloqot)
2. **Mantiq qatlami** — `backend/` (qoidalar, AI)
3. **Ma'lumot qatlami** — baza (jadvallar)

## 2.2. Backend modullari (har fayl bitta vazifa)

```mermaid
flowchart TD
    main[main.py<br/>API manzillar] --> schemas[schemas.py<br/>ma'lumot tekshiruvi]
    main --> services[services.py<br/>biznes qoidalar]
    main --> ai[ai.py<br/>sun'iy intellekt]
    services --> models[models.py<br/>jadvallar]
    main --> models
    models --> database[database.py<br/>bazaga ulanish]
    seed[seed.py<br/>boshlang'ich ma'lumot] --> models
    seed --> ai
```

## 2.3. Use-case diagrammasi (foydalanish holatlari)

```mermaid
flowchart LR
    G([Mehmon])
    A([Admin])
    AI([Hugging Face AI])

    G --- UC1(Xonalarni ko'rish va qidirish)
    G --- UC2(AI bilan qidirish)
    G --- UC3(Xonani bron qilish)
    G --- UC4(Bronni ko'rish va bekor qilish)
    G --- UC5(Sharh qoldirish)
    G --- UC6(AI chat bilan suhbat)
    A --- UC7(Statistikani ko'rish)
    A --- UC8(Barcha bronlarni ko'rish)

    UC2 -.-> AI
    UC5 -.-> AI
    UC6 -.-> AI
```

## 2.4. ER diagramma (baza tuzilishi)

```mermaid
erDiagram
    ROOMS ||--o{ BOOKINGS : "bron qilinadi"
    ROOMS ||--o{ REVIEWS : "sharh oladi"

    ROOMS {
        int id PK
        string code "SGL, DBL, TWN, ACC, DLX, FAM, JSU, PRS"
        string name
        string room_type "standard, deluxe, family, suite"
        int price_per_night
        int capacity
        int quantity "shu turdagi xonalar soni"
        int size_m2
        string bed_type
        string view
        int floor
        string floors "masalan 3-6"
        string suited_for "solo, couple, family ..."
        string amenities
        text description
        string image_url
    }
    BOOKINGS {
        int id PK
        int room_id FK
        string guest_name
        string guest_email
        string guest_phone
        date check_in
        date check_out
        int guests
        int total_price
        string status "confirmed, cancelled"
        datetime created_at
    }
    REVIEWS {
        int id PK
        int room_id FK
        string author
        int rating "1-5"
        text comment
        string sentiment "AI: positive, neutral, negative"
        float sentiment_score
        datetime created_at
    }
```

**Indekslar** (qidiruvni tezlashtirish uchun): `bookings(room_id, check_in, check_out)`, `bookings(guest_email)`, `reviews(room_id)`.

## 2.5. Ketma-ketlik diagrammasi: bron qilish

```mermaid
sequenceDiagram
    actor M as Mehmon
    participant F as Frontend (app.js)
    participant B as Backend (main.py)
    participant S as services.py
    participant D as Baza

    M->>F: Formani to'ldirib "Bron qilish"
    F->>B: POST /api/bookings (JSON)
    B->>B: Pydantic: ma'lumotni tekshirish
    B->>B: Qoidalar: sana, 30 kecha, sig'im
    B->>S: is_room_available(xona turi, sanalar)  — quantity − eng band kecha > 0
    S->>D: Kesishuvchi bronlar bormi?
    D-->>S: soni
    alt xona band
        B-->>F: 409 "Bu xona tanlangan sanalarda band"
        F-->>M: Xato xabari
    else bo'sh
        B->>D: Bronni saqlash
        B-->>F: 200 + bron kodi (SR-2026-00001)
        F-->>M: "Bron tasdiqlandi"
    end
```

## 2.6. AI qidiruv oqimi

```mermaid
sequenceDiagram
    actor M as Mehmon
    participant F as Frontend
    participant B as Backend
    participant A as ai.py
    participant H as Hugging Face

    M->>F: "Oilam bilan 4 kishi, balkonli, 160$ gacha"
    F->>B: POST /api/ai/recommend
    B->>A: parse_request(matn)
    A->>H: "Matndan JSON filtr ajrat"
    alt AI javob berdi
        H-->>A: {"guests":4,"max_price":160,...}
    else xato / sekin / token yo'q
        A->>A: Zaxira: regex + kalit so'zlar
    end
    A-->>B: filtrlar
    B->>B: Bo'sh xonalarni olish (2 ta so'rov)
    B->>B: rank_rooms: ball berib saralash
    B-->>F: filtrlar + eng mos 4 xona
    F-->>M: "AI tushundi: 4 kishi, 160$ gacha..." + xonalar
```

## 2.7. Loyihalash qarorlari va sabablari
| Qaror | Sabab |
|---|---|
| Frontend va backend alohida | Har biri alohida joylanadi va rivojlanadi; Netlify/Railway'ga mos |
| FastAPI | Python'da yoziladi, avtomatik hujjat (`/docs`) va ma'lumot tekshiruvi bor |
| SQLAlchemy ORM | SQLite ↔ PostgreSQL ni kodni o'zgartirmasdan almashtirish mumkin |
| `services.py` ajratilgan | Qoidalarni API'dan alohida sinash va tushuntirish oson |
| AI + zaxira rejim | AI tashqi xizmat, uning uzilishi tizimni to'xtatmasligi kerak |
| AI'ga bazadagi xonalar ro'yxati beriladi | AI o'zidan narx/xona to'qib chiqarmasligi uchun |
