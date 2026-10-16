"""
tools/make_hotel_svg.py — mehmonxona binosining RASMINI (SVG) yaratadi.

Ishlatish (loyiha papkasidan):   python tools/make_hotel_svg.py
Natija: frontend/img/hotel-illustration.svg

Rasmda: nomi yozilgan bino (9 qavat, har qavat raqami bilan), bosh kirish soyaboni, favvorali maydon,
formadagi eshik oldi xizmatchisi va valet xodimlari, mashina, valet posti, yer osti avtoturargoh (-1, -2 qavat).
Bu o'zimiz chizgan original rasm (hech qaysi haqiqiy bino nusxasi emas).
Sayt bu faylni yuklab, qavatlarni bosiladigan qiladi (frontend/app.js → "8) Bino rasmi").
"""
import os
import random

W, H = 1200, 800
GROUND = 650                      # ko'cha sathi
X0, X1 = 330, 870                 # bino chap va o'ng chegarasi
FLOOR_H, LOBBY_H = 50, 70
GREEN, GOLD, INK = "#0f3d2e", "#c8963e", "#1d2a25"
rnd = random.Random(7)            # har safar bir xil rasm chiqishi uchun
out = []


def add(s):
    out.append(s)


def floor_top(n):
    """n-qavatning yuqori chizig'i (1-qavat — lobby)."""
    return GROUND - LOBBY_H - (n - 1) * FLOOR_H


def person(x, base, coat, trim, hat, label):
    """Oddiy xodim figurasi: forma rangi, oltin tugma, bosh kiyim, ismi yozilgan nishon."""
    add(f'<g><title>{label}</title>')
    add(f'<rect x="{x-7}" y="{base-20}" width="6" height="20" fill="#1d2a25"/><rect x="{x+1}" y="{base-20}" width="6" height="20" fill="#1d2a25"/>')   # oyoq
    add(f'<rect x="{x-9}" y="{base-48}" width="18" height="30" rx="4" fill="{coat}"/>')                                                                  # kurtka
    add(f'<rect x="{x-13}" y="{base-46}" width="5" height="22" rx="2" fill="{coat}"/><rect x="{x+8}" y="{base-46}" width="5" height="22" rx="2" fill="{coat}"/>')   # qo'l
    add(f'<circle cx="{x}" cy="{base-40}" r="1.6" fill="{trim}"/><circle cx="{x}" cy="{base-33}" r="1.6" fill="{trim}"/><circle cx="{x}" cy="{base-26}" r="1.6" fill="{trim}"/>')  # tugma
    add(f'<rect x="{x+2}" y="{base-44}" width="6" height="3" fill="#fff"/>')                                                                              # nishon
    add(f'<circle cx="{x}" cy="{base-56}" r="7" fill="#e8b98f"/>')                                                                                        # bosh
    if hat == "cap":
        add(f'<path d="M{x-8} {base-58} a8 7 0 0 1 16 0 z" fill="{coat}"/><rect x="{x-9}" y="{base-59}" width="18" height="3" fill="{trim}"/><rect x="{x-9}" y="{base-57}" width="13" height="2" fill="{coat}"/>')
    else:   # doorman: yuqori qalpoq
        add(f'<rect x="{x-8}" y="{base-67}" width="16" height="10" rx="2" fill="{coat}"/><rect x="{x-9}" y="{base-60}" width="18" height="3" fill="{trim}"/>')
    add('</g>')


def pill(x, y, text):
    w = len(text) * 6 + 14
    add(f'<rect x="{x - w/2}" y="{y-12}" width="{w}" height="17" rx="8" fill="#fffdf8" stroke="{GOLD}" opacity=".95"/>'
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="10.5" fill="{INK}" font-weight="600">{text}</text>')


def car(x, base, color, scale=1.0, rot=0):
    s = scale
    add(f'<g transform="translate({x} {base}) rotate({rot}) scale({s})"><title>Mehmon mashinasi</title>'
        f'<rect x="0" y="-26" width="110" height="16" rx="6" fill="{color}"/>'
        f'<path d="M22 -26 L34 -42 L76 -42 L90 -26 Z" fill="{color}"/>'
        f'<path d="M30 -27 L38 -39 L55 -39 L55 -27 Z M59 -27 L59 -39 L74 -39 L84 -27 Z" fill="#cfe6f2"/>'
        f'<rect x="102" y="-22" width="6" height="5" fill="#ffe9a8"/><rect x="2" y="-22" width="5" height="5" fill="#d96a5a"/>'
        f'<circle cx="26" cy="-9" r="9" fill="#222"/><circle cx="26" cy="-9" r="4" fill="#aaa"/>'
        f'<circle cx="85" cy="-9" r="9" fill="#222"/><circle cx="85" cy="-9" r="4" fill="#aaa"/></g>')


def tree(x, base, r=34):
    add(f'<rect x="{x-4}" y="{base-r-8}" width="8" height="{r+8}" fill="#6b4a2b"/>'
        f'<circle cx="{x}" cy="{base-r-14}" r="{r}" fill="#3f7d4f"/><circle cx="{x-r*0.5}" cy="{base-r+2}" r="{r*0.65}" fill="#4a8d5a"/>'
        f'<circle cx="{x+r*0.55}" cy="{base-r+2}" r="{r*0.65}" fill="#356f45"/>')


# ----------------------------------------------------------------------------------------------
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="Silk Road Grand Hotel binosi: 9 qavat, favvora, valet xodimlari va yer osti avtoturargoh" '
    f'font-family="Inter, Arial, sans-serif">')
add('''<style>
  .floor { cursor: pointer; outline: none; }
  .floor .floor-bg { transition: fill .15s; }
  .floor:hover .floor-bg, .floor:focus-visible .floor-bg { fill: #f6e7bd; }
  .floor.sel .floor-bg { fill: #f3dc9a; }
  .floor.sel .tag-circle, .floor:hover .tag-circle, .floor:focus-visible .tag-circle { fill: #c8963e; }
  .jet { stroke-dasharray: 6 5; animation: jet 1s linear infinite; }
  @keyframes jet { to { stroke-dashoffset: -22; } }
  @media (prefers-reduced-motion: reduce) { .jet { animation: none; } }
</style>
<defs>
  <linearGradient id="hsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bfe0ee"/><stop offset="1" stop-color="#f6f1e7"/></linearGradient>
  <linearGradient id="hwater" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fd8ee"/><stop offset="1" stop-color="#4f9fc4"/></linearGradient>
</defs>''')

# osmon, quyosh, bulutlar
add(f'<rect width="{W}" height="{GROUND}" fill="url(#hsky)"/>')
add('<circle cx="1070" cy="95" r="34" fill="#f4c95d"/>')
for cx, cy, rx in [(190, 110, 60), (250, 100, 44), (900, 70, 56), (960, 80, 40), (120, 230, 40)]:
    add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{rx*0.4}" fill="#fff" opacity=".85"/>')

# yer: maysazor, ko'cha, yer osti qismi
add(f'<rect x="0" y="{GROUND}" width="{W}" height="18" fill="#7d8580"/>')                       # asfalt
add(f'<rect x="0" y="{GROUND}" width="{W}" height="4" fill="#a9b0ab"/>')                        # yo'l bo'yi
for i in range(0, W, 70):
    add(f'<rect x="{i}" y="{GROUND+11}" width="36" height="3" fill="#f2f2ee"/>')                # yo'l chizig'i
add(f'<rect x="0" y="{GROUND+18}" width="{W}" height="{H-GROUND-18}" fill="#5b4a37"/>')         # tuproq
add(f'<rect x="20" y="{GROUND-8}" width="290" height="8" rx="4" fill="#5fa86b"/>')              # maysazor (favvora atrofi)

# ---- Bino ----
add(f'<g id="svg-building">')
# sahifa ustida: tom, yozuv, yulduzlar
roof_y = floor_top(9) - 14
add(f'<rect x="{X0-12}" y="{roof_y}" width="{X1-X0+24}" height="14" fill="#7a6a48"/>')
add(f'<rect x="{X0+20}" y="{roof_y-52}" width="{X1-X0-40}" height="50" rx="6" fill="{GREEN}"/>')
add(f'<rect x="{X0+20}" y="{roof_y-52}" width="{X1-X0-40}" height="50" rx="6" fill="none" stroke="{GOLD}" stroke-width="2"/>')
add(f'<text x="600" y="{roof_y-26}" text-anchor="middle" font-family="Fraunces, Georgia, serif" font-weight="700" font-size="32" fill="{GOLD}" '
    f'letter-spacing="8">SILK ROAD</text>')
add(f'<text x="600" y="{roof_y-9}" text-anchor="middle" font-family="Fraunces, Georgia, serif" font-weight="600" font-size="15" fill="#fff" '
    f'letter-spacing="6">GRAND HOTEL</text>')
add(f'<text x="600" y="{roof_y-62}" text-anchor="middle" font-size="22" fill="{GOLD}" letter-spacing="6">★ ★ ★ ★</text>')

# yon ustunlar
add(f'<rect x="{X0-8}" y="{roof_y+14}" width="14" height="{GROUND-roof_y-14}" fill="#d3c39c"/>')
add(f'<rect x="{X1-6}" y="{roof_y+14}" width="14" height="{GROUND-roof_y-14}" fill="#d3c39c"/>')

for n in range(9, 1, -1):          # 9..2-qavat
    top = floor_top(n)
    has_balcony = n in (5, 6, 7, 8)
    add(f'<g class="floor" data-floor="{n}" tabindex="0" role="button" aria-label="{n}-qavat haqida ma\'lumot"><title>{n}-qavat</title>')
    add(f'<rect class="floor-bg" x="{X0}" y="{top}" width="{X1-X0}" height="{FLOOR_H}" fill="#e9dfc9" stroke="#cbbd9b"/>')
    for i in range(6):
        wx = 362 + i * 80
        lit = rnd.random() < 0.3
        add(f'<rect x="{wx}" y="{top+9}" width="52" height="28" rx="2" fill="{"#ffe9a8" if lit else "#7fb2c9"}" stroke="#8d7f5f"/>')
        add(f'<line x1="{wx+26}" y1="{top+9}" x2="{wx+26}" y2="{top+37}" stroke="#8d7f5f"/>')
        if has_balcony:
            add(f'<rect x="{wx-4}" y="{top+36}" width="60" height="9" fill="none" stroke="#6f6244" stroke-width="1.5"/>'
                f'<line x1="{wx-4}" y1="{top+40}" x2="{wx+56}" y2="{top+40}" stroke="#6f6244"/>')
    add(f'<circle class="tag-circle" cx="298" cy="{top+25}" r="15" fill="{GREEN}"/>'
        f'<text x="298" y="{top+30}" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">{n}</text>')
    add('</g>')

# 1-qavat: lobby va kirish
top = floor_top(1)
add(f'<g class="floor" data-floor="1" tabindex="0" role="button" aria-label="1-qavat (lobby) haqida ma\'lumot"><title>1-qavat: lobby</title>')
add(f'<rect class="floor-bg" x="{X0}" y="{top}" width="{X1-X0}" height="{LOBBY_H}" fill="#e9dfc9" stroke="#cbbd9b"/>')
for gx in (350, 690):      # katta shisha oynalar
    add(f'<rect x="{gx}" y="{top+14}" width="160" height="{LOBBY_H-14}" fill="#9cc7d9" stroke="#6f6244" stroke-width="2"/>')
    for k in range(1, 4):
        add(f'<line x1="{gx+k*40}" y1="{top+14}" x2="{gx+k*40}" y2="{GROUND}" stroke="#6f6244"/>')
add(f'<rect x="558" y="{top+20}" width="84" height="{LOBBY_H-20}" fill="#cfe6f2" stroke="{GOLD}" stroke-width="3"/>')   # eshik
add(f'<line x1="600" y1="{top+20}" x2="600" y2="{GROUND}" stroke="{GOLD}" stroke-width="2"/>')
add(f'<path d="M515 {top+18} L685 {top+18} L700 {top+6} L500 {top+6} Z" fill="{GREEN}" stroke="{GOLD}" stroke-width="2"/>')   # soyabon
add(f'<text x="600" y="{top+15}" text-anchor="middle" font-size="9" font-weight="700" fill="{GOLD}" letter-spacing="3">KIRISH · RESEPSHN 24/7</text>')
add(f'<circle class="tag-circle" cx="298" cy="{top+35}" r="15" fill="{GREEN}"/><text x="298" y="{top+40}" text-anchor="middle" font-size="14" font-weight="700" fill="#fff">1</text>')
add('</g>')
add('</g>')   # /building

# ---- Yer osti avtoturargoh (kesim) ----
UG1, UG2 = GROUND + 18, GROUND + 68
for n, y in ((-1, UG1), (-2, UG2)):
    add(f'<g class="floor" data-floor="{n}" tabindex="0" role="button" aria-label="{n}-qavat (avtoturargoh) haqida ma\'lumot"><title>{n}-qavat: avtoturargoh</title>')
    add(f'<rect class="floor-bg" x="{X0}" y="{y}" width="{X1-X0}" height="50" fill="#38433d" stroke="#222"/>')
    for px in range(X0 + 45, X1, 90):
        add(f'<rect x="{px-4}" y="{y}" width="8" height="50" fill="#56635b"/>')
    for k, cx in enumerate((372, 462, 552, 642, 732, 800)):
        if (n == -1 and k == 4) or (n == -2 and k in (1, 3)):
            continue                               # bo'sh o'rin
        col = ["#b9534a", "#4f7cac", "#d9d3c4", "#3f7d4f", "#c8963e", "#8a6fb0"][(k + abs(n)) % 6]
        car(cx - 8, y + 47, col, 0.62)
    add(f'<circle class="tag-circle" cx="298" cy="{y+25}" r="15" fill="{GREEN}"/><text x="298" y="{y+30}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">{n}</text>')
    add('</g>')
add(f'<g><title>Elektromobil quvvatlash</title><rect x="{X0+6}" y="{UG1+8}" width="18" height="30" rx="3" fill="#3fbf6f"/>'
    f'<text x="{X0+15}" y="{UG1+28}" text-anchor="middle" font-size="14" fill="#fff">⚡</text></g>')
add(f'<g><title>Nogironlar uchun o\'rin</title><rect x="{X1-30}" y="{UG1+8}" width="22" height="22" rx="3" fill="#2d6cdf"/>'
    f'<text x="{X1-19}" y="{UG1+25}" text-anchor="middle" font-size="14" fill="#fff">♿</text></g>')
# yo'l (pandus) — ko'chadan yer ostiga
add(f'<polygon points="{X1},{UG1} 1010,{GROUND+18} 1010,{GROUND+18} {X1},{UG2+50}" fill="#2a322d"/>')
add(f'<polygon points="{X1},{UG1} 1010,{GROUND+18} {X1+130},{GROUND+18}" fill="#2a322d"/>')
car(X1 + 28, UG1 + 55, "#4f7cac", 0.5, 24)
add(f'<rect x="1000" y="{GROUND-118}" width="5" height="118" fill="#555"/><rect x="976" y="{GROUND-148}" width="54" height="40" rx="6" fill="#2d6cdf"/>'
    f'<text x="1003" y="{GROUND-120}" text-anchor="middle" font-size="30" font-weight="700" fill="#fff">P</text>')
pill(1003, GROUND - 160, "Avtoturargoh ↓")

# ---- Favvorali maydon ----
fx = 170
add(f'<g id="svg-fountain"><title>Favvora</title>')
add(f'<ellipse cx="{fx}" cy="{GROUND-10}" rx="108" ry="16" fill="#cfc7b4" stroke="#a79d86"/>')               # katta havza chetidagi tosh
add(f'<ellipse cx="{fx}" cy="{GROUND-14}" rx="98" ry="12" fill="url(#hwater)"/>')
add(f'<rect x="{fx-9}" y="{GROUND-64}" width="18" height="52" fill="#cfc7b4" stroke="#a79d86"/>')            # ustun
add(f'<ellipse cx="{fx}" cy="{GROUND-52}" rx="48" ry="9" fill="#cfc7b4" stroke="#a79d86"/><ellipse cx="{fx}" cy="{GROUND-54}" rx="42" ry="6" fill="url(#hwater)"/>')   # o'rta havza
add(f'<rect x="{fx-5}" y="{GROUND-96}" width="10" height="44" fill="#cfc7b4" stroke="#a79d86"/>')
add(f'<ellipse cx="{fx}" cy="{GROUND-92}" rx="24" ry="5" fill="#cfc7b4" stroke="#a79d86"/>')
for dx, h in ((0, 46), (-16, 30), (16, 30), (-30, 18), (30, 18)):                                          # suv oqimlari
    add(f'<path class="jet" d="M{fx+dx*0.2} {GROUND-96} Q{fx+dx*0.6} {GROUND-96-h} {fx+dx} {GROUND-54}" fill="none" stroke="#bfe6f6" stroke-width="3" stroke-linecap="round"/>')
add('</g>')
pill(fx, GROUND - 124, "Favvora")
tree(40, GROUND, 30)
tree(310, GROUND, 28)

# ---- Valet posti, mashina va xodimlar ----
add(f'<g><title>Valet posti</title><rect x="900" y="{GROUND-62}" width="62" height="62" fill="#e9dfc9" stroke="#8d7f5f"/>'
    f'<rect x="894" y="{GROUND-72}" width="74" height="12" fill="{GREEN}" stroke="{GOLD}"/>'
    f'<text x="931" y="{GROUND-63}" text-anchor="middle" font-size="9" font-weight="700" fill="{GOLD}" letter-spacing="2">VALET</text>'
    f'<rect x="906" y="{GROUND-50}" width="26" height="22" fill="#9cc7d9" stroke="#6f6244"/>'
    f'<rect x="938" y="{GROUND-50}" width="18" height="50" fill="#6f6244"/></g>')
car(722, GROUND + 14, "#b9534a")                                           # eshik oldidagi mashina
person(692, GROUND + 14, GREEN, GOLD, "cap", "Valet xodimi: mashinani avtoturargohga olib boradi")
person(545, GROUND + 14, GREEN, GOLD, "tall", "Eshik oldi xizmatchisi")
person(875, GROUND + 14, GREEN, GOLD, "cap", "Valet xodimi")
pill(931, GROUND - 82, "Valet posti")

# o'ng tomondagi daraxtlar
tree(1110, GROUND, 30)
tree(1170, GROUND, 24)

# sarlavha
add(f'<rect x="20" y="20" width="250" height="34" rx="8" fill="#fffdf8" opacity=".92"/><text x="34" y="42" font-size="14" font-weight="600" fill="{INK}">Silk Road Grand Hotel · bino ko\'rinishi</text>')
add('</svg>')

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "img", "hotel-illustration.svg")
with open(path, "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("Yaratildi:", os.path.normpath(path), f"({os.path.getsize(path)//1024} KB)")
