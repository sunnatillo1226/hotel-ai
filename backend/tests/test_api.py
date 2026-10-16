"""
test_api.py — asosiy funksiyalarni avtomatik tekshiradi.
Ishga tushirish (backend papkasida):   pytest -v
"""
from datetime import date, timedelta

ADMIN = {"X-Admin-Key": "test-key"}


def d(days):
    """Bugundan `days` kun keyingi sana (matn ko'rinishida)."""
    return str(date.today() + timedelta(days=days))


def rid(client, code):
    """Xona turining id sini kodi (SGL, DBL, DLX, FAM, PRS ...) bo'yicha topadi."""
    return next(r["id"] for r in client.get("/api/rooms").json() if r["code"] == code)


def book(client, room="DLX", start=10, end=12, guests=2, email="ali@mail.com", **extra):
    """room — xona kodi (matn) yoki id (son). Hujjat bron uchun shart, shuning uchun sukut bo'yicha qo'shiladi."""
    room_id = rid(client, room) if isinstance(room, str) else room
    body = {"room_id": room_id, "guest_name": "Ali Valiyev", "guest_email": email,
            "check_in": d(start), "check_out": d(end), "guests": guests,
            "doc_type": "passport", "doc_number": "AB1234567"}
    body.update(extra)
    return client.post("/api/bookings", json=body)


# ---------------- Xonalar ----------------
def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"
    assert r.json()["ai_enabled"] is False          # testda token yo'q -> zaxira rejim


def test_rooms_list_sorted_by_price(client):
    rooms = client.get("/api/rooms").json()
    assert len(rooms) == 8                       # 8 xona turi (jami 84 xona)
    prices = [x["price_per_night"] for x in rooms]
    assert prices == sorted(prices)


def test_rooms_filter_by_guests(client):
    rooms = client.get("/api/rooms?guests=4").json()
    assert rooms and all(x["capacity"] >= 4 for x in rooms)


def test_rooms_have_rating_from_seed_reviews(client):
    room = client.get(f"/api/rooms/{rid(client, 'DLX')}").json()
    assert room["review_count"] == 1 and room["avg_rating"] == 5.0


def test_unknown_room_404(client):
    assert client.get("/api/rooms/999").status_code == 404


# ---------------- Bron qilish ----------------
def test_booking_success_and_price(client):
    r = book(client, "DLX", start=10, end=13)         # Deluxe 95$ x 3 kecha
    assert r.status_code == 200
    body = r.json()
    assert body["total_price"] == 285
    assert body["code"].startswith("SR-") and body["status"] == "confirmed"


def test_quantity_limits_overlapping_bookings(client):
    """Prezident Suite'dan 2 ta bor: ikkita bron o'tadi, uchinchisi (sanasi kesishsa) rad etiladi."""
    assert book(client, "PRS", start=10, end=14, guests=2, email="a@mail.com").status_code == 200
    assert book(client, "PRS", start=12, end=15, guests=2, email="b@mail.com").status_code == 200
    assert book(client, "PRS", start=13, end=14, guests=2, email="c@mail.com").status_code == 409
    assert book(client, "PRS", start=20, end=22, guests=2, email="c@mail.com").status_code == 200   # boshqa sana


def test_back_to_back_booking_allowed(client):
    """Bir mehmon 14-kuni chiqadi, ikkinchisi 14-kuni kiradi — bu ruxsat etilishi kerak (PRS: 2 ta bor)."""
    for _ in range(2):
        assert book(client, "PRS", start=10, end=14).status_code == 200
    assert book(client, "PRS", start=14, end=16, email="boshqa@mail.com").status_code == 200


def test_remaining_and_availability_flag(client):
    book(client, "PRS", start=10, end=12)
    rooms = {x["code"]: x for x in client.get(f"/api/rooms?check_in={d(10)}&check_out={d(12)}").json()}
    assert rooms["PRS"]["remaining"] == 1 and rooms["PRS"]["available"] is True
    book(client, "PRS", start=10, end=12, email="b@mail.com")
    rooms = {x["code"]: x for x in client.get(f"/api/rooms?check_in={d(10)}&check_out={d(12)}").json()}
    assert rooms["PRS"]["available"] is False and rooms["PRS"]["remaining"] == 0
    assert rooms["SGL"]["available"] is True and rooms["SGL"]["remaining"] == 12
    # faqat bo'shlarini so'rasak PRS ro'yxatda bo'lmaydi
    only = client.get(f"/api/rooms?check_in={d(10)}&check_out={d(12)}&only_available=true").json()
    assert all(x["code"] != "PRS" for x in only)


def test_suited_for_filter(client):
    fam = {x["code"] for x in client.get("/api/rooms?suited_for=family").json()}
    assert "FAM" in fam and "SGL" not in fam
    acc = client.get("/api/rooms?suited_for=accessible").json()
    assert any(x["code"] == "ACC" for x in acc)


def test_hotel_profile(client):
    h = client.get("/api/hotel").json()
    assert h["rooms_total"] == 84 and h["room_types"] == 8 and h["stars"] == 4
    assert h["check_in"] == "14:00" and h["floors_above"] == 9
    assert any("Avtoturargoh" in g["group"] for g in h["facilities"])
    titles = [c["title"] for c in h["documents"]["cards"]]
    assert any("Er-xotin" in t for t in titles) and any("Oilalar" in t for t in titles)
    assert len(h["audiences"]) == 7 and h["photo_credits"]


def test_hotel_building_staff_and_floors(client):
    """Bino rasmi va xodimlar bo'limi uchun ma'lumot: qavatlar, favvora/valet, forma."""
    h = client.get("/api/hotel").json()
    floors = {f["floor"]: f for f in h["floors"]}
    assert set(floors) == {9, 8, 7, 6, 5, 4, 3, 2, 1, -1, -2}
    assert sorted(r["code"] for r in floors[9]["room_types"]) == ["JSU", "PRS"]   # eng yuqori qavat — suite qavati
    assert floors[1]["room_types"] == [] and "resepshn" in floors[1]["what"].lower()
    assert "favvora" in h["entrance"]["fountain"].lower() and "valet" in h["entrance"]["valet"].lower()
    roles = " ".join(p["role"] for p in h["staff"])
    assert "Valet" in roles and "Eshik oldi" in roles and all(p["uniform"] and p["colors"] for p in h["staff"])


def test_ai_chat_valet_and_fountain(client):
    def ask(q):
        return client.post("/api/ai/chat", json={"messages": [{"role": "user", "content": q}]}).json()["answer"]
    assert "olib keladi" in ask("Valet xizmati qanday?")
    assert "favvora" in ask("Mehmonxona oldida favvora bormi?").lower()


def test_booking_validation(client):
    assert book(client, start=-3, end=-1).status_code == 400            # o'tgan sana
    assert book(client, start=10, end=10).status_code == 400            # 0 kecha
    assert book(client, "SGL", guests=2).status_code == 400             # sig'maydi (Single: 1 kishi)
    assert book(client, start=10, end=45).status_code == 400            # 30 kechadan ko'p
    assert book(client, start=400, end=402).status_code == 400          # 1 yildan uzoq
    assert book(client, 999).status_code == 404                 # xona yo'q
    assert book(client, email="notanemail").status_code == 422          # email noto'g'ri


def test_booking_requires_identity_document(client):
    """Shaxsni tasdiqlovchi hujjat turi va raqamisiz bron qilib bo'lmaydi."""
    room_id = rid(client, "DLX")
    base = {"room_id": room_id, "guest_name": "Ali Valiyev", "guest_email": "ali@mail.com",
            "check_in": d(10), "check_out": d(12), "guests": 2}
    assert client.post("/api/bookings", json=base).status_code == 422                                   # hujjat yo'q
    assert client.post("/api/bookings", json={**base, "doc_type": "passport", "doc_number": "12"}).status_code == 422   # juda qisqa
    assert client.post("/api/bookings", json={**base, "doc_type": "library_card", "doc_number": "AB1234567"}).status_code == 422
    ok = client.post("/api/bookings", json={**base, "doc_type": "id_card", "doc_number": "AA 7654321"})
    assert ok.status_code == 200
    body = ok.json()
    assert body["doc_type"] == "id_card" and body["doc_number_masked"].endswith("321")
    assert "7654321" not in str(body)                       # to'liq raqam API javobida chiqmaydi


def test_couple_needs_marriage_certificate(client):
    """Er-xotin sifatida joylashish uchun nikoh guvohnomasi raqami shart; do'stlar uchun shart emas."""
    assert book(client, "DBL", is_couple=True).status_code == 422                                      # guvohnoma yo'q
    assert book(client, "DBL", is_couple=True, marriage_cert_number="  ").status_code == 422
    assert book(client, "SGL", guests=1, is_couple=True, marriage_cert_number="I-TN 123456").status_code in (400, 422)   # 1 mehmon er-xotin bo'lolmaydi
    ok = book(client, "DBL", is_couple=True, marriage_cert_number="I-TN 123456")
    assert ok.status_code == 200 and ok.json()["is_couple"] is True
    friends = book(client, "TWN", email="d@mail.com")                                                  # er-xotin emas -> guvohnoma kerak emas
    assert friends.status_code == 200 and friends.json()["is_couple"] is False


def test_cancel_frees_room_and_checks_owner(client):
    booking = book(client, start=10, end=12).json()
    assert client.post(f"/api/bookings/{booking['id']}/cancel?email=x@mail.com").status_code == 404
    assert client.post(f"/api/bookings/{booking['id']}/cancel?email=ali@mail.com").status_code == 200
    assert client.post(f"/api/bookings/{booking['id']}/cancel?email=ali@mail.com").status_code == 400  # ikki marta emas
    assert book(client, start=10, end=12, email="boshqa@mail.com").status_code == 200   # xona bo'shadi


def test_my_bookings_email_is_case_insensitive(client):
    book(client, email="Ali@Mail.com")
    items = client.get("/api/bookings?email=ALI@mail.com").json()
    assert len(items) == 1 and items[0]["room_name"].startswith("Deluxe")


# ---------------- Sharhlar (AI sentiment, zaxira rejim) ----------------
def test_review_sentiment(client):
    good = client.post("/api/reviews", json={"room_id": rid(client, "SGL"), "author": "Ali", "rating": 5,
                                              "comment": "Juda toza va qulay, rahmat!"}).json()
    bad = client.post("/api/reviews", json={"room_id": rid(client, "SGL"), "author": "Vali", "rating": 1,
                                             "comment": "Iflos va shovqin, yomon xizmat"}).json()
    assert good["sentiment"] == "positive" and bad["sentiment"] == "negative"


def test_review_validation(client):
    r = client.post("/api/reviews", json={"room_id": 1, "author": "Ali", "rating": 9, "comment": "yaxshi"})
    assert r.status_code == 422


# ---------------- AI ----------------
def test_ai_recommend_family_first(client):
    r = client.post("/api/ai/recommend", json={"text": "Oilam bilan 4 kishi, balkonli xona kerak, 160$ gacha"}).json()
    assert r["filters"]["guests"] == 4 and r["filters"]["max_price"] == 160
    assert r["rooms"][0]["name"] == "Family xona"
    assert all(x["capacity"] >= 4 and x["price_per_night"] <= 160 for x in r["rooms"])


def test_ai_keyword_not_matched_inside_word(client):
    """"gacha" so'zi ichidagi "ac" konditsioner deb tushunilmasligi kerak (avval shunday xato bor edi)."""
    f = client.post("/api/ai/recommend", json={"text": "100$ gacha xona kerak"}).json()["filters"]
    assert "konditsioner" not in f["amenities"]


def test_ai_recommend_skips_fully_booked_type(client):
    prs = rid(client, "PRS")
    book(client, "PRS", start=10, end=12)
    book(client, "PRS", start=10, end=12, email="b@mail.com")          # ikkala Prezident Suite band
    r = client.post("/api/ai/recommend", json={"text": "lyuks suite kerak", "check_in": d(10), "check_out": d(12)}).json()
    assert all(x["id"] != prs for x in r["rooms"])


def test_ai_detects_audience(client):
    r = client.post("/api/ai/recommend", json={"text": "turmush o'rtog'im bilan asal oyiga, balkonli xona"}).json()
    assert r["filters"]["audience"] == "couple" and "balkon" in r["filters"]["amenities"]
    assert r["rooms"] and "couple" in r["rooms"][0]["suited_for"]
    f = client.post("/api/ai/recommend", json={"text": "nogironlar uchun xona kerak"}).json()["filters"]
    assert f["audience"] == "accessible"


def test_ai_chat_documents_and_parking(client):
    def ask(q):
        return client.post("/api/ai/chat", json={"messages": [{"role": "user", "content": q}]}).json()["answer"]
    answer = ask("Er-xotin bo'lsak nikoh guvohnomasi kerakmi?").lower()
    assert "nikoh" in answer and "kerak" in answer and "pasport" in answer
    assert "BEPUL" in ask("Mashina qo'yadigan joy bormi?")


def test_ai_chat_fallback(client):
    r = client.post("/api/ai/chat", json={"messages": [{"role": "user", "content": "Chiqish vaqti qachon?"}]}).json()
    assert "12:00" in r["answer"] and r["source"] == "fallback"


# ---------------- Admin va tezlik ----------------
def test_admin_requires_key(client):
    assert client.get("/api/admin/stats").status_code == 401
    assert client.get("/api/admin/stats", headers={"X-Admin-Key": "wrong"}).status_code == 401
    assert client.get("/api/admin/stats", headers=ADMIN).status_code == 200


def test_admin_stats_numbers(client):
    book(client, "DLX", start=10, end=12)              # 95$ x 2 = 190$
    s = client.get("/api/admin/stats", headers=ADMIN).json()
    assert s["confirmed_bookings"] == 1 and s["revenue"] == 190 and s["total_rooms"] == 84


def test_response_time_header_and_gzip(client):
    r = client.get("/api/rooms", headers={"Accept-Encoding": "gzip"})
    assert "x-process-time" in r.headers
    assert r.headers.get("content-encoding") == "gzip"


def test_rooms_have_multiple_photos(client):
    """Har bir xona turida kamida 3 ta surat (yotoqxona, hammom va h.k.) va birinchisi asosiy surat."""
    for r in client.get("/api/rooms").json():
        assert len(r["images"]) >= 3, r["code"]
        assert r["images"][0]["src"] == r["image_url"]
        assert all(i["caption"] for i in r["images"])


def test_hotel_gallery_welcome_and_balcony(client):
    """Galereya (lobby, koridor, oshxona, zal, yashil hudud), kutib olish xizmati va balkon ko'rinishi."""
    import os
    h = client.get("/api/hotel").json()
    groups = {g["group"] for g in h["gallery"]}
    assert {"Lobby", "Yo'laklar", "Restoran va oshxona", "Zallar", "Yashil hudud"} <= groups
    assert len(h["welcome"]["steps"]) == 5
    # balkon: teleminora CHAPDA, xiyobon O'NGDA (koordinatalardan hisoblangan)
    assert h["balcony_view"]["sides_ok"] is True
    # barcha surat fayllari diskda bor
    root = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
    paths = [g["src"] for g in h["gallery"]] + [s["image"] for s in h["welcome"]["steps"]] + [h["balcony_view"]["image"]]
    paths += [i["src"] for r in client.get("/api/rooms").json() for i in r["images"]]
    assert all(os.path.exists(os.path.join(root, p)) for p in paths)


def test_distances_computed_from_coordinates(client):
    d = {x["place"]: x for x in client.get("/api/hotel").json()["distances"]}
    assert 3.0 < d["Toshkent teleminorasi"]["km"] < 4.5
    assert d["Amir Temur xiyoboni va maydoni"]["km"] < 1


def test_chat_welcome_and_balcony(client):
    def ask(q):
        return client.post("/api/ai/chat", json={"messages": [{"role": "user", "content": q}]}).json()["answer"]
    a = ask("Kutib olish xizmati qanday?")
    assert "doorman" in a.lower() and "bellboy" in a.lower()
    b = ask("Balkondan teleminora ko'rinadimi?")
    assert "teleminora" in b.lower()


def test_floors_are_separated_by_guest_type(client):
    """Qavatlar toifalar bo'yicha ajratilgan: oilalar alohida qavatda, boshqa tur aralashmaydi."""
    floors = {f["floor"]: sorted(r["code"] for r in f["room_types"]) for f in client.get("/api/hotel").json()["floors"]}
    assert floors[3] == ["FAM"]                       # oilalar faqat 3-qavatda, yolg'iz boshqa tur yo'q
    assert floors[2] == ["ACC"]                       # moslashgan xonalar — liftga yaqin past qavat
    assert floors[4] == ["SGL"] and floors[7] == ["TWN"] and floors[8] == ["DLX"]
    assert floors[5] == floors[6] == ["DBL"]
    rooms = client.get("/api/rooms").json()
    fam = next(r for r in rooms if r["code"] == "FAM")
    assert fam["floors"] == "3"
    assert sum(r["quantity"] for r in rooms) == 84


def test_chat_family_floor_and_location(client):
    def ask(q):
        return client.post("/api/ai/chat", json={"messages": [{"role": "user", "content": q}]}).json()["answer"]
    assert "3-qavat" in ask("Oilam uchun qaysi qavat bor?")
    assert "teleminorasi" in ask("Mehmonxona manzili qayerda?").lower()


# ---------------- AI suhbat sifati (chatbot.py) ----------------
def chat(client, *turns):
    """turns: ketma-ket foydalanuvchi savollari; oldingi javoblar tarixga qo'shiladi. Oxirgi javobni qaytaradi."""
    messages, data = [], {}
    for q in turns:
        messages.append({"role": "user", "content": q})
        data = client.post("/api/ai/chat", json={"messages": messages}).json()
        messages.append({"role": "assistant", "content": data["answer"]})
    return data


def test_chat_airport_transfer_is_not_welcome_service(client):
    """Avval 'transfer' so'zi kutib olish xizmatiga noto'g'ri yo'naltirardi."""
    a = chat(client, "Aeroportdan transfer bormi?")["answer"]
    assert "15$" in a and "bellboy" not in a


def test_chat_named_room_and_followup_context(client):
    assert "130$" in chat(client, "Family xona qancha turadi?")["answer"]
    assert "3-qavat" in chat(client, "Family xona qancha turadi?", "va qavati?")["answer"]     # oldingi xonani eslab qoladi
    assert "narxlar" not in chat(client, "Deluxe xona haqida ayt")["answer"].lower()
    all_prices = chat(client, "Family xona qancha turadi?", "barcha xonalar narxlari")["answer"]
    assert "Single" in all_prices and "Prezident" in all_prices                             # umumiy savol -> hamma narxlar


def test_chat_recommends_rooms_from_request(client):
    a = chat(client, "2 kishi, 100$ gacha xona tavsiya qiling")["answer"]
    assert "Double" in a and "Prezident" not in a
    assert "nechta mehmon" in chat(client, "menga xona kerak")["answer"].lower()               # kam ma'lumot -> aniqlashtiradi


def test_chat_languages_follow_the_user(client):
    assert "Breakfast" in chat(client, "Do you have breakfast?")["answer"]
    assert "парковка" in chat(client, "Есть ли парковка?")["answer"].lower()
    assert "Assalomu" in chat(client, "Salom")["answer"]


def test_chat_suggestions_and_out_of_scope(client):
    r = chat(client, "Salom")
    assert 1 <= len(r["suggestions"]) <= 3 and all(isinstance(s, str) for s in r["suggestions"])
    off = chat(client, "bugun ob-havo qanday?")
    assert "resepshn" in off["answer"].lower() and off["suggestions"]


def test_chat_never_asks_for_or_repeats_personal_data(client):
    r = chat(client, "pasportim AB1234567")
    assert "AB1234567" not in r["answer"] and "yozmang" in r["answer"]
    assert r["source"] == "fallback"                                                          # AI'ga yuborilmaydi


def test_chat_input_validation(client):
    assert client.post("/api/ai/chat", json={"messages": []}).status_code == 422
    assert client.post("/api/ai/chat", json={"messages": [{"role": "system", "content": "x"}]}).status_code == 422
    assert client.post("/api/ai/chat", json={"messages": [{"role": "user", "content": "a" * 1001}]}).status_code == 422
