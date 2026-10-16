"""
main.py — PyCharm'da BITTA tugma (yashil ▶ Run) bilan butun loyihani ishga tushiradi.

Nima qiladi (ketma-ket):
  1) Kutubxonalar (fastapi, uvicorn, sqlalchemy ...) o'rnatilmagan bo'lsa, o'zi o'rnatadi (backend/requirements.txt)
  2) Eski hotel.db bazasi yangi versiyaga mos kelmasa, uni zaxira nusxaga o'tkazadi
  3) Backend serverini ishga tushiradi  -> http://127.0.0.1:8000   (API hujjati: /docs)
  4) Sayt serverini ishga tushiradi      -> http://localhost:5500
  5) Brauzerda saytni ochadi

To'xtatish: PyCharm'dagi qizil ■ (Stop) tugmasi.
Loyiha tuzilishi: README.md va docs/06-fayllar-xaritasi.md
"""
import atexit
import importlib.util
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
FRONTEND = os.path.join(ROOT, "frontend")
API_URL = "http://127.0.0.1:8000"
SITE_URL = "http://localhost:5500"
children = []


def say(msg):
    print(f"[Mehmonxona] {msg}", flush=True)


def alive(url):
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.status == 200
    except (OSError, ValueError):          # ulanib bo'lmadi / vaqt tugadi — server hali yo'q
        return False


def ensure_packages():
    """Kutubxonalar bormi? Yo'q bo'lsa, pip bilan o'rnatadi (birinchi marta 1-2 daqiqa olishi mumkin)."""
    needed = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "requests", "dotenv", "email_validator"]
    if all(importlib.util.find_spec(name) for name in needed):
        say("Kutubxonalar tayyor.")
    else:
        say("Kutubxonalar o'rnatilmoqda... (bir necha daqiqa kuting)")
        cmd = [sys.executable, "-m", "pip", "install", "-r", os.path.join(BACKEND, "requirements.txt")]
        if subprocess.call(cmd) != 0:
            say("XATO: kutubxonalarni o'rnatib bo'lmadi. Internet bor-yo'qligini tekshiring.")
            sys.exit(1)
        say("Kutubxonalar o'rnatildi.")


def check_database():
    """Eski versiyadagi hotel.db yangi ustunlarga ega emas: uni nusxalab chetga olib qo'yamiz (ma'lumot yo'qolmaydi)."""
    path = os.path.join(BACKEND, "hotel.db")
    if not os.path.exists(path):
        return
    import sqlite3
    con = sqlite3.connect(path)
    try:
        def cols(table):
            return [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
        rooms, bookings = cols("rooms"), cols("bookings")
        stale = bool(rooms) and ("images" not in rooms or "code" not in rooms)
        stale = stale or (bool(bookings) and "doc_type" not in bookings)
    finally:
        con.close()
    if stale:
        backup = path + f".eski-{int(time.time())}"
        shutil.move(path, backup)
        say(f"Eski baza yangi versiyaga mos emas: nusxasi saqlandi ({os.path.basename(backup)}), yangi baza yaratiladi.")


def start(name, args, cwd):
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONPATH="")   # ildizdagi main.py backend/main.py bilan aralashmasin
    p = subprocess.Popen([sys.executable, *args], cwd=cwd, env=env)
    children.append(p)
    say(f"{name} ishga tushdi (PID {p.pid}).")
    return p


def stop_all():
    for p in children:
        if p.poll() is None:
            p.terminate()
    for p in children:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()


def on_signal(signum, frame):
    """Ctrl+C yoki PyCharm'dagi Stop bosilganda: serverlarni to'xtatib chiqamiz."""
    stop_all()
    sys.exit(0)


def main():
    say("Boshlandi.")
    ensure_packages()
    check_database()
    atexit.register(stop_all)
    for sig in ("SIGINT", "SIGTERM", "SIGBREAK"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), on_signal)

    if alive(API_URL + "/api/health"):
        say("Backend allaqachon ishlayapti (8000-port) — qayta yoqilmaydi.")
    else:
        start("Backend", ["-m", "uvicorn", "main:app", "--port", "8000"], BACKEND)
    if alive(SITE_URL):
        say("Sayt serveri allaqachon ishlayapti (5500-port).")
    else:
        start("Sayt serveri", ["-m", "http.server", "5500"], FRONTEND)

    for _ in range(40):                      # backend tayyor bo'lishini kutamiz (eng ko'pi 20 soniya)
        if alive(API_URL + "/api/health"):
            break
        time.sleep(0.5)
    else:
        say("OGOHLANTIRISH: backend javob bermadi. Yuqoridagi xato xabarlarni o'qing.")

    say(f"TAYYOR!  Sayt: {SITE_URL}   |   API hujjati: {API_URL}/docs   |   Admin: {SITE_URL}/admin.html")
    webbrowser.open(SITE_URL)
    say("To'xtatish uchun qizil ■ (Stop) tugmasini bosing.")
    try:
        while any(p.poll() is None for p in children) or not children:
            time.sleep(1)
            if not children:
                time.sleep(3600)
    except KeyboardInterrupt:
        pass
    finally:
        stop_all()


if __name__ == "__main__":
    main()
