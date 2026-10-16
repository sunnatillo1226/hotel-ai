/* app.js — saytning BARCHA JavaScript mantig'i (mehmon sahifasi, index.html).
   Backend bilan gaplashadi (fetch), natijani sahifaga chizadi. Alohida fayllarga bo'linmagan — bo'limlar tartib bilan.
   Tuzilishi:  1) yordamchi funksiyalar  2) xonalar  3) AI qidiruv  4) xona oynasi (bron + sharh)
               5) mening bronlarim  6) AI chat  7) mehmonxona haqida (GET /api/hotel)
               8) bino rasmi (qavatlarni bosish)  9) xodimlar va valet
*/
const API = window.APP_CONFIG.API_URL;

/* ============ 1) Yordamchi funksiyalar ============ */

// Backendga so'rov yuborish. Xato bo'lsa, tushunarli matn bilan Error tashlaydi.
async function api(path, options = {}) {
  let res;
  try {
    res = await fetch(API + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Serverga ulanib bo'lmadi. Backend ishlayotganini tekshiring.");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    // FastAPI: oddiy xato -> detail: "matn", validatsiya xatosi -> detail: [ ... ]
    // Pydantic validatori o'z xabarini beradi ("Value error, ...") — foydalanuvchiga aynan shuni ko'rsatamiz
    const first = Array.isArray(data.detail) ? data.detail[0] : null;
    const own = first && /^Value error, /.test(first.msg || "") ? first.msg.replace("Value error, ", "") : "";
    const field = first && first.loc ? first.loc[first.loc.length - 1] : "";
    const FIELD = { doc_number: "Hujjat raqami", doc_type: "Hujjat turi", guest_name: "Ism", guest_email: "Email", guests: "Mehmonlar soni" };
    const detail = Array.isArray(data.detail)
      ? (own || (FIELD[field] ? `${FIELD[field]} noto'g'ri kiritilgan` : "Ma'lumotlar noto'g'ri kiritilgan"))
      : data.detail;
    throw new Error(detail || "Xatolik yuz berdi");
  }
  return data;
}

// Foydalanuvchi kiritgan matnni xavfsiz qilish (XSS'dan himoya)
const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const $ = (id) => document.getElementById(id);

// Qisqa xabar (alert o'rniga): sahifani to'xtatib qo'ymaydi, o'zi yo'qoladi
let toastTimer;
function toast(message, isError = false) {
  const el = $("toast");
  el.textContent = message;
  el.className = "toast" + (isError ? " err" : "");
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (el.hidden = true), 4500);
}

// Ma'lumot kelguncha "skelet" kartalarni ko'rsatamiz — sayt tezroq his qilinadi
function showSkeleton(count = 6) {
  $("roomGrid").innerHTML = Array.from({ length: count }, () =>
    '<div class="skeleton"><div class="sk-img"></div><div class="sk-line"></div><div class="sk-line short"></div><div class="sk-line"></div></div>').join("");
  $("roomsEmpty").hidden = true;
}
const toISO = (d) => d.toISOString().slice(0, 10);
const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const nightsBetween = (a, b) => Math.round((new Date(b) - new Date(a)) / 86400000);

const TYPE_ICON = { standard: "🛏️", deluxe: "🌇", family: "👨‍👩‍👧‍👦", suite: "👑" };
const TYPE_NAME = { standard: "Standart", deluxe: "Deluxe", family: "Oilaviy", suite: "Suite" };
const AMENITY_ICON = { wifi: "📶 Wi-Fi", tv: "📺 TV", konditsioner: "❄️ Konditsioner", balkon: "🌇 Balkon", jakuzi: "🛁 Jakuzi",
  minibar: "🥤 Minibar", nonushta: "🍳 Nonushta", sejf: "🔒 Sejf", manzara: "🏙️ Manzara", choynak: "☕ Choynak",
  fen: "💨 Fen", xalat: "🥋 Xalat", "ish-stoli": "💻 Ish stoli", "kofe-mashina": "☕ Kofe mashina",
  "divan-karavot": "🛋️ Divan-karavot", "bolalar-beshigi": "👶 Bolalar beshigi", "moslashgan-hammom": "♿ Moslashgan hammom" };
const SENT = { positive: "😊 Ijobiy", neutral: "😐 Neytral", negative: "😞 Salbiy" };

/* ============ 2) Xonalar ============ */

const state = { checkIn: "", checkOut: "", guests: 2, rooms: [], reqId: 0, audience: "", hotel: null, datesChosen: false, catalog: [] };
// "couple" -> "Er-xotin / juftlik" (nomlar /api/hotel dan keladi)
const audienceTitle = (key) => (state.hotel?.audiences || []).find((a) => a.key === key)?.title || key;

function initDates() {
  const today = new Date();
  $("fCheckIn").min = toISO(today);
  $("fCheckOut").min = toISO(addDays(today, 1));
  $("fCheckIn").value = state.checkIn = toISO(addDays(today, 1));
  $("fCheckOut").value = state.checkOut = toISO(addDays(today, 3));
  $("fCheckIn").addEventListener("change", () => {
    // Chiqish sanasi har doim kirishdan keyin bo'lsin
    const min = toISO(addDays(new Date($("fCheckIn").value), 1));
    $("fCheckOut").min = min;
    if ($("fCheckOut").value < min) $("fCheckOut").value = min;
  });
}

function photo(r, cls = "photo") {
  // Rasm yuklanmasa (xato) — pastdagi gradient va emoji ko'rinib turadi, sayt buzilmaydi
  return r.image_url ? `<img class="${cls}" src="${esc(r.image_url)}" alt="${esc(r.name)}" width="800" height="533" loading="lazy">` : "";
}

function stockLine(r) {
  if (r.remaining === null || r.remaining === undefined) return `<span class="chip">🏨 Jami ${r.quantity} ta xona</span>`;
  if (r.remaining === 0) return '<span class="chip stock-out">Bu sanalarda qolmagan</span>';
  return `<span class="chip ${r.remaining <= 3 ? "stock-low" : "stock-ok"}">Qolgan: ${r.remaining} xona</span>`;
}

function roomCard(r) {
  const status = r.available === true ? '<span class="badge ok">Bo\'sh</span>' : r.available === false ? '<span class="badge bad">Band</span>' : "";
  const rating = r.avg_rating ? `⭐ ${r.avg_rating} (${r.review_count})` : "Yangi";
  const amenities = r.amenities.slice(0, 4).map((a) => `<span class="chip">${esc(AMENITY_ICON[a] || a)}</span>`).join("");
  const reasons = (r.match_reasons || []).map((x) => `<span class="chip match">✓ ${esc(x)}</span>`).join("");
  const suited = (r.suited_for || []).slice(0, 3).map((k) => `<span class="chip suited">${esc(audienceTitle(k))}</span>`).join("");
  return `
    <article class="card ${r.available === false ? "unavailable" : ""}" data-id="${r.id}">
      <div class="banner t-${esc(r.room_type)}"><span class="ico">${TYPE_ICON[r.room_type] || "🛏️"}</span>${photo(r)}<span class="code">${esc(r.code)}</span>${status}</div>
      <div class="card-body">
        <div class="card-top"><h3>${esc(r.name)}</h3><span class="rating">${rating}</span></div>
        <p class="desc">${esc(r.description)}</p>
        <div class="specs"><span>📐 ${r.size_m2} m²</span><span>🛏️ ${esc(r.bed_type)}</span><span>🪟 ${esc(r.view)}</span></div>
        <div class="meta"><span class="chip">👥 ${r.capacity} kishigacha</span><span class="chip">🏢 ${esc(r.floors)}-qavat</span>${stockLine(r)}</div>
        ${suited ? `<div class="meta">${suited}</div>` : ""}
        <div class="meta">${amenities}</div>
        ${reasons ? `<div class="meta">${reasons}</div>` : ""}
        <div class="card-foot">
          <div class="price">$${r.price_per_night} <small>/ kecha</small></div>
          <button class="btn" type="button">Batafsil</button>
        </div>
      </div>
    </article>`;
}

function renderRooms(rooms) {
  state.rooms = rooms;
  $("roomGrid").innerHTML = rooms.map(roomCard).join("");
  $("roomsEmpty").hidden = rooms.length > 0;
}

async function loadRooms(useFilters = false) {
  const params = new URLSearchParams();
  if (useFilters) {
    state.checkIn = $("fCheckIn").value;
    state.checkOut = $("fCheckOut").value;
    state.guests = $("fGuests").value;
    params.set("check_in", state.checkIn);
    params.set("check_out", state.checkOut);
    params.set("guests", state.guests);
    if ($("fType").value) params.set("room_type", $("fType").value);
  }
  if (state.audience) params.set("suited_for", state.audience);
  const myReq = ++state.reqId;                       // oxirgi so'rovnigina ko'rsatamiz (poyga holatidan himoya)
  showSkeleton();
  const slowTimer = setTimeout(() => ($("slowNote").hidden = false), 3000);   // bepul serverlar uxlab qolishi mumkin
  try {
    const rooms = await api("/api/rooms?" + params);
    if (myReq !== state.reqId) return;
    renderRooms(rooms);
    if (!useFilters && !state.audience) state.catalog = rooms;      // to'liq ro'yxat: bino rasmidan xona ochish uchun
    $("aiFilters").hidden = true;
    $("roomsTitle").textContent = useFilters ? "Qidiruv natijalari" : "Bizning xona turlari";
    $("roomsSub").textContent = useFilters
      ? `${state.checkIn} → ${state.checkOut} · ${nightsBetween(state.checkIn, state.checkOut)} kecha`
      : "";
  } catch (e) {
    if (myReq !== state.reqId) return;
    $("roomGrid").innerHTML = "";
    $("roomsEmpty").hidden = false;
    $("roomsEmpty").textContent = e.message;
  } finally {
    clearTimeout(slowTimer);
    $("slowNote").hidden = true;
  }
}

$("searchForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if ($("fCheckOut").value <= $("fCheckIn").value) return toast("Chiqish sanasi kirish sanasidan keyin bo'lishi kerak", true);
  state.datesChosen = true;
  await loadRooms(true);
  $("rooms").scrollIntoView();
});

// Karta bosilganda xona oynasini ochish (event delegation)
$("roomGrid").addEventListener("click", (e) => {
  const card = e.target.closest(".card");
  if (card) openRoom(Number(card.dataset.id));
});

/* ============ 3) AI qidiruv ============ */

$("aiForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = $("aiText").value.trim();
  if (text.length < 3) return;
  const btn = e.submitter || e.target.querySelector("button");
  btn.disabled = true; btn.textContent = "Qidirilmoqda...";
  try {
    const body = { text };
    // Sana tanlangan bo'lsa, faqat bo'sh xonalarni olish uchun yuboramiz
    if ($("fCheckIn").value && $("fCheckOut").value > $("fCheckIn").value) {
      body.check_in = $("fCheckIn").value; body.check_out = $("fCheckOut").value;
      state.checkIn = body.check_in; state.checkOut = body.check_out;
    }
    const data = await api("/api/ai/recommend", { method: "POST", body: JSON.stringify(body) });
    renderRooms(data.rooms);

    // AI nimani tushunganini ko'rsatamiz — foydalanuvchi ishonch hosil qiladi
    const f = data.filters, parts = [];
    if (f.guests) parts.push(`${f.guests} kishi`);
    if (f.max_price) parts.push(`${f.max_price}$ gacha`);
    if (f.room_type) parts.push(`tur: ${TYPE_NAME[f.room_type]}`);
    if (f.audience) parts.push(`kim uchun: ${audienceTitle(f.audience)}`);
    (f.amenities || []).forEach((a) => parts.push(AMENITY_ICON[a] || a));
    $("aiFilters").innerHTML = `<strong>✨ ${f.source === "ai" ? "AI" : "Aqlli qidiruv"} tushundi:</strong> ` +
      (parts.length ? parts.map((p) => `<span class="chip">${esc(p)}</span>`).join("") : "aniq talab topilmadi") +
      `<span class="muted">· eng mos xonalar yuqorida</span>`;
    $("aiFilters").hidden = false;
    $("roomsTitle").textContent = "Siz uchun tanlangan xonalar";
    $("roomsSub").textContent = "";
    $("rooms").scrollIntoView();
  } catch (err) {
    toast(err.message, true);
  } finally {
    btn.disabled = false; btn.textContent = "AI bilan topish";
  }
});

/* ============ 4) Xona oynasi: bron + sharhlar ============ */

const dlg = $("roomDialog");
$("dlgClose").addEventListener("click", () => dlg.close());
dlg.addEventListener("click", (e) => { if (e.target === dlg) dlg.close(); }); // tashqarisini bosganda yopish

async function openRoom(id) {
  const room = state.rooms.find((r) => r.id === id) || state.catalog.find((r) => r.id === id);
  if (!room) return;
  const reviews = await api(`/api/rooms/${id}/reviews`).catch(() => []);
  const amenities = room.amenities.map((a) => `<span class="chip">${esc(AMENITY_ICON[a] || a)}</span>`).join("");
  const reviewsHtml = reviews.length
    ? reviews.map((v) => `
        <div class="review">
          <div class="review-head"><strong>${esc(v.author)}</strong>
            <span>${"⭐".repeat(v.rating)} <span class="sent ${esc(v.sentiment)}" title="AI tahlili">${SENT[v.sentiment] || ""}</span></span></div>
          ${esc(v.comment)}
        </div>`).join("")
    : '<p class="muted">Hali sharhlar yo\'q. Birinchi bo\'ling!</p>';

  $("dlgBody").innerHTML = `
    <div class="dlg-banner t-${esc(room.room_type)}"><span class="ico">${TYPE_ICON[room.room_type] || "🛏️"}</span>${photo(room, "photo")}<span class="dlg-cap" id="dlgCap">${esc(room.images?.[0]?.caption || "")}</span></div>
    ${(room.images || []).length > 1 ? `<div class="dlg-thumbs" id="dlgThumbs" role="group" aria-label="Xona suratlari">${room.images.map((im, i) =>
      `<button type="button" data-i="${i}" class="${i === 0 ? "on" : ""}" aria-label="${esc(im.caption)}"><img src="${esc(im.src)}" alt="${esc(im.caption)}" loading="lazy"><span>${esc(im.caption)}</span></button>`).join("")}</div>` : ""}
    <div class="dlg-content">
      <div>
        <h2>${esc(room.name)} <small class="code-inline">${esc(room.code)}</small></h2>
        <p class="muted">${esc(room.description)}</p>
        <ul class="spec-list">
          <li>📐 <b>${room.size_m2} m²</b></li><li>🛏️ ${esc(room.bed_type)}</li><li>🪟 ${esc(room.view)}</li>
          <li>🏢 ${esc(room.floors)}-qavat</li><li>👥 ${room.capacity} kishigacha</li><li>🏨 Jami ${room.quantity} ta shunday xona</li>
        </ul>
        <div class="meta">${(room.suited_for || []).map((k) => `<span class="chip suited">${esc(audienceTitle(k))}</span>`).join("")}</div>
        <div class="meta" style="margin-top:8px">${amenities}</div>
      </div>

      <form id="bookForm" class="form-grid">
        <label>Ism familiya <input name="guest_name" required minlength="2" autocomplete="name" placeholder="Ali Valiyev"></label>
        <label>Email <input name="guest_email" type="email" required autocomplete="email" placeholder="ali@mail.com"></label>
        <label>Telefon <input name="guest_phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+998 90 123 45 67"></label>
        <label>Mehmonlar soni <input name="guests" type="number" min="1" max="${room.capacity}" value="${Math.min(state.guests || 2, room.capacity)}" required></label>
        <label>Kirish <input name="check_in" type="date" required min="${toISO(new Date())}" value="${state.checkIn}"></label>
        <label>Chiqish <input name="check_out" type="date" required min="${toISO(new Date())}" value="${state.checkOut}"></label>
        <fieldset class="doc-fields">
          <h4>🪪 Shaxsni tasdiqlovchi hujjat (majburiy)</h4>
          <label>Hujjat turi
            <select name="doc_type" required>
              <option value="passport">Pasport (O'zbekiston)</option>
              <option value="id_card">ID-karta</option>
              <option value="foreign_passport">Xalqaro / chet el pasporti</option>
            </select></label>
          <label>Hujjat raqami <input name="doc_number" required minlength="5" maxlength="20" autocomplete="off" placeholder="AB1234567"></label>
          <label class="check"><input type="checkbox" name="is_couple"> Biz er-xotinmiz (juftlik sifatida joylashamiz)</label>
          <label id="certWrap" hidden>Nikoh guvohnomasi raqami <input name="marriage_cert_number" minlength="3" maxlength="40" autocomplete="off" placeholder="Guvohnoma raqami"></label>
          <p class="muted small" style="grid-column:1/-1;margin:0">Hujjat raqami faqat ro'yxatdan o'tkazish uchun saqlanadi va keyin faqat oxirgi 3 raqami ko'rsatiladi. Joylashishda asl hujjat ko'rsatiladi.</p>
        </fieldset>
        <div class="total-box full"><span id="nightsInfo"></span><strong id="totalInfo"></strong></div>
        <p class="muted small full">ℹ️ Check-in ${esc(state.hotel?.check_in || "14:00")} dan, check-out ${esc(state.hotel?.check_out || "12:00")} gacha.
          Bron uchun <b>pasport/ID raqami</b> kiritiladi, joylashishda asli ko'rsatiladi. <b>Er-xotinlardan nikoh guvohnomasi</b> so'raladi. 24 soat oldin bepul bekor qilish.</p>
        <div id="bookMsg" class="full" hidden></div>
        <button class="btn full" type="submit">Bron qilish</button>
      </form>

      <div>
        <h3>Mehmonlar sharhlari</h3>
        <div id="reviewList">${reviewsHtml}</div>
      </div>

      <details class="rev-add">
        <summary>Sharh qoldirish</summary>
        <form id="reviewForm" class="form-grid" style="margin-top:12px">
          <label>Ismingiz <input name="author" required minlength="2"></label>
          <label>Baho <select name="rating"><option value="5">⭐⭐⭐⭐⭐ A'lo</option><option value="4">⭐⭐⭐⭐ Yaxshi</option>
            <option value="3">⭐⭐⭐ O'rtacha</option><option value="2">⭐⭐ Yomon</option><option value="1">⭐ Juda yomon</option></select></label>
          <label class="full">Sharh <textarea name="comment" rows="3" required minlength="3"></textarea></label>
          <div id="revMsg" class="full" hidden></div>
          <button class="btn full" type="submit">Yuborish (AI kayfiyatini aniqlaydi)</button>
        </form>
      </details>
    </div>`;

  const form = $("bookForm");
  const recalc = () => {
    const n = nightsBetween(form.elements.check_in.value, form.elements.check_out.value);
    const tooLong = n > 30;                       // backend ham shu qoidani tekshiradi
    $("nightsInfo").textContent = tooLong ? "Eng ko'pi bilan 30 kecha" : n > 0 ? `${n} kecha × $${room.price_per_night}` : "Sanalarni to'g'ri tanlang";
    $("totalInfo").textContent = n > 0 && !tooLong ? `Jami: $${n * room.price_per_night}` : "";
  };
  const couple = form.elements.is_couple, certWrap = $("certWrap");
  couple.addEventListener("change", () => {
    certWrap.hidden = !couple.checked;
    form.elements.marriage_cert_number.required = couple.checked;
    if (couple.checked && Number(form.elements.guests.value) < 2) form.elements.guests.value = Math.min(2, room.capacity);
  });
  $("dlgThumbs")?.addEventListener("click", (e) => {
    const b = e.target.closest("[data-i]");
    if (!b) return;
    const im = room.images[Number(b.dataset.i)];
    document.querySelector("#dlgBody .dlg-banner .photo").src = im.src;
    $("dlgCap").textContent = im.caption;
    $("dlgThumbs").querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b));
  });
  form.elements.check_in.addEventListener("change", recalc);
  form.elements.check_out.addEventListener("change", recalc);
  recalc();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const box = $("bookMsg"), btn = form.querySelector("button[type=submit]");
    btn.disabled = true; box.hidden = true;
    const body = {
      room_id: room.id,
      guest_name: form.elements.guest_name.value.trim(),
      guest_email: form.elements.guest_email.value.trim(),
      guest_phone: form.elements.guest_phone.value.trim(),
      check_in: form.elements.check_in.value,
      check_out: form.elements.check_out.value,
      guests: Number(form.elements.guests.value),
      doc_type: form.elements.doc_type.value,
      doc_number: form.elements.doc_number.value.trim(),
      is_couple: form.elements.is_couple.checked,
      marriage_cert_number: form.elements.is_couple.checked ? form.elements.marriage_cert_number.value.trim() : null,
    };
    try {
      const b = await api("/api/bookings", { method: "POST", body: JSON.stringify(body) });
      box.className = "msg good full";
      box.innerHTML = `✅ Bron tasdiqlandi! Bron kodi: <strong>${esc(b.code)}</strong> · ${esc(b.room_name)} · ${b.check_in} → ${b.check_out} · jami <strong>$${b.total_price}</strong>.<br>Bronlarni "Mening bronlarim" bo'limida email orqali ko'rishingiz mumkin.`;
      $("myEmail").value = b.guest_email;
      form.querySelectorAll("input").forEach((i) => (i.disabled = true));
      btn.hidden = true;
    } catch (err) {
      box.className = "msg err full"; box.textContent = "⚠️ " + err.message;
      btn.disabled = false;
    }
    box.hidden = false;
  });

  $("reviewForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const f = e.target, box = $("revMsg");
    try {
      const v = await api("/api/reviews", { method: "POST", body: JSON.stringify({
        room_id: room.id, author: f.elements.author.value.trim(), rating: Number(f.elements.rating.value), comment: f.elements.comment.value.trim() }) });
      box.className = "msg good full";
      box.textContent = `Rahmat! AI sharhingizni shunday baholadi: ${SENT[v.sentiment]}`;
      f.reset();
      const list = await api(`/api/rooms/${room.id}/reviews`);
      $("reviewList").innerHTML = list.map((x) => `
        <div class="review"><div class="review-head"><strong>${esc(x.author)}</strong>
        <span>${"⭐".repeat(x.rating)} <span class="sent ${esc(x.sentiment)}">${SENT[x.sentiment] || ""}</span></span></div>${esc(x.comment)}</div>`).join("");
    } catch (err) {
      box.className = "msg err full"; box.textContent = "⚠️ " + err.message;
    }
    box.hidden = false;
  });

  dlg.showModal();
}

/* ============ 5) Mening bronlarim ============ */

async function loadMyBookings(email) {
  const list = $("myList");
  try {
    const items = await api("/api/bookings?email=" + encodeURIComponent(email));
    if (!items.length) { list.innerHTML = '<p class="empty">Bu email bo\'yicha bron topilmadi.</p>'; return; }
    list.innerHTML = items.map((b) => `
      <div class="booking ${b.status}">
        <div>
          <strong>${esc(b.code)} · ${esc(b.room_name)}</strong>
          <div class="muted">${b.check_in} → ${b.check_out} · ${b.guests} kishi · $${b.total_price}</div>
        </div>
        <div style="display:flex;gap:10px;align-items:center">
          <span class="status ${b.status}">${b.status === "confirmed" ? "Tasdiqlangan" : "Bekor qilingan"}</span>
          ${b.status === "confirmed" ? `<button class="btn btn-ghost" data-cancel="${b.id}" data-email="${esc(email)}">Bekor qilish</button>` : ""}
        </div>
      </div>`).join("");
  } catch (err) {
    list.innerHTML = `<p class="empty">${esc(err.message)}</p>`;
  }
}

$("myForm").addEventListener("submit", (e) => { e.preventDefault(); loadMyBookings($("myEmail").value.trim()); });

$("myList").addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-cancel]");
  if (!btn || !confirm("Bronni bekor qilishni xohlaysizmi?")) return;
  try {
    await api(`/api/bookings/${btn.dataset.cancel}/cancel?email=${encodeURIComponent(btn.dataset.email)}`, { method: "POST" });
    loadMyBookings(btn.dataset.email);
  } catch (err) { toast(err.message, true); }
});

/* ============ 6) AI chat ============ */

const chat = { messages: [] };
function addBubble(role, text, source) {
  const div = document.createElement("div");
  div.className = "bubble " + (role === "user" ? "me" : "bot");
  div.textContent = text;
  if (source) {
    const s = document.createElement("small");
    s.textContent = source === "ai" ? "AI javobi" : "tayyor javob";
    div.appendChild(s);
  }
  $("chatLog").appendChild(div);
  $("chatLog").scrollTop = $("chatLog").scrollHeight;
  return div;
}

// Javobdan keyin "keyingi savol" tugmalarini ko'rsatadi (bosilsa o'sha savol yuboriladi)
function showSuggestions(list) {
  if (!list || !list.length) return;
  const box = $("chatQuick");
  box.replaceChildren();
  list.forEach((q) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = q;
    box.appendChild(b);
  });
}

let chatBusy = false;
async function sendChat(text) {
  if (chatBusy) return;                 // oldingi javob kelmaguncha yangi savol yuborilmaydi
  chatBusy = true;
  addBubble("user", text);
  chat.messages.push({ role: "user", content: text });
  const typing = addBubble("assistant", "...");
  try {
    const data = await api("/api/ai/chat", { method: "POST", body: JSON.stringify({ messages: chat.messages.slice(-20) }) });
    typing.remove();
    addBubble("assistant", data.answer, data.source);
    chat.messages.push({ role: "assistant", content: data.answer });
    showSuggestions(data.suggestions);
  } catch (err) {
    chat.messages.pop();                // xato bo'lsa, savol tarixdan olib tashlanadi — qayta urinish mumkin
    typing.textContent = "⚠️ " + err.message + " Resepshn: " + (state.hotel && state.hotel.phone ? state.hotel.phone : "+998 71 000 00 00");
  } finally {
    chatBusy = false;
  }
}

$("chatFab").addEventListener("click", () => {
  $("chatPanel").hidden = false; $("chatFab").hidden = true;
  if (!$("chatLog").children.length) addBubble("assistant", "Assalomu alaykum! Men mehmonxona AI yordamchisiman. Xona, narx yoki xizmatlar haqida so'rang 🙂");
  $("chatInput").focus();
});
function closeChat() { $("chatPanel").hidden = true; $("chatFab").hidden = false; $("chatFab").focus(); }
$("chatClose").addEventListener("click", closeChat);
document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("chatPanel").hidden) closeChat(); });
$("chatForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const text = $("chatInput").value.trim();
  if (!text) return;
  $("chatInput").value = "";
  sendChat(text);
});
$("chatQuick").addEventListener("click", (e) => { if (e.target.tagName === "BUTTON") sendChat(e.target.textContent); });

/* ============ 7) Mehmonxona haqida: GET /api/hotel ============ */

function renderAudienceBar(audiences) {
  const all = [{ key: "", title: "Hammasi", icon: "✨" }, ...audiences];
  $("audienceBar").innerHTML = all.map((a) =>
    `<button type="button" class="aud-chip${a.key === state.audience ? " on" : ""}" data-aud="${esc(a.key)}" aria-pressed="${a.key === state.audience}">${a.icon} ${esc(a.title)}</button>`).join("");
}

$("audienceBar").addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-aud]");
  if (!btn) return;
  state.audience = btn.dataset.aud;
  renderAudienceBar(state.hotel?.audiences || []);
  const hint = (state.hotel?.audiences || []).find((a) => a.key === state.audience)?.hint;
  $("audienceHint").textContent = hint || "";
  $("audienceHint").hidden = !hint;
  await loadRooms(state.datesChosen);
});

function renderHotel(h) {
  state.hotel = h;
  $("heroTag").textContent = `Toshkent markazida · ${"★".repeat(h.stars)} mehmonxona`;
  const facts = [`${"★".repeat(h.stars)} ${h.stars} yulduzli`, `🏢 ${h.floors_above} qavat`, `🛏️ ${h.rooms_total} xona`,
    "🛎️ 24/7 resepshn", "🅿️ Bepul yopiq avtoturargoh", "📶 Bepul Wi-Fi"];
  $("heroFacts").innerHTML = facts.map((f) => `<li>${esc(f)}</li>`).join("");
  $("aboutSub").textContent = h.tagline;
  $("layoutList").innerHTML = h.layout.map((l) => `<li><b>${esc(l.floor)}-qavat</b><span>${esc(l.what)}</span></li>`).join("");
  $("facilityGrid").innerHTML = h.facilities.map((g) =>
    `<div class="fac"><h3>${g.icon} ${esc(g.group)}</h3><ul>${g.items.map((i) => `<li>${esc(i)}</li>`).join("")}</ul></div>`).join("");
  $("addressLine").textContent = h.address;
  $("distanceList").innerHTML = h.distances.map((d) => `<li><span>${d.icon}</span><div><b>${esc(d.place)}</b><br>${esc(d.value)}${d.note ? `<br><span class="muted small">${esc(d.note)}</span>` : ""}</div></li>`).join("");
  const pad = 0.006;
  $("mapFrame").src = `https://www.openstreetmap.org/export/embed.html?bbox=${h.longitude - pad * 1.6},${h.latitude - pad},${h.longitude + pad * 1.6},${h.latitude + pad}&layer=mapnik&marker=${h.latitude},${h.longitude}`;
  $("coords").textContent = `Koordinatalar: ${h.latitude.toFixed(4)}° N, ${h.longitude.toFixed(4)}° E · masofalar to'g'ri chiziq bo'yicha hisoblangan. Joy namunaviy tanlangan.`;
  $("mapLink").href = `https://www.openstreetmap.org/?mlat=${h.latitude}&mlon=${h.longitude}#map=16/${h.latitude}/${h.longitude}`;
  $("docNote").textContent = h.documents.note;
  $("docGrid").innerHTML = h.documents.cards.map((c) =>
    `<div class="doc"><h3>${c.icon} ${esc(c.title)}</h3><ul>${c.points.map((p) => `<li>${esc(p)}</li>`).join("")}</ul></div>`).join("");
  $("docSource").textContent = "Manba: " + h.documents.source;
  $("policyList").innerHTML = h.policies.map((p) => `<div><dt>${esc(p.title)}</dt><dd>${esc(p.text)}</dd></div>`).join("");
  $("demoNote").textContent = h.demo_note;
  $("credits").innerHTML = h.photo_credits.map((c) => `<a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.author)}</a>`).join(", ");
  renderAudienceBar(h.audiences);
  renderEntrance(h);
  renderStaff(h);
  renderFloors(h);
  renderWelcome(h);
  renderGallery(h);
  renderBalcony(h);
  if (state.rooms.length) renderRooms(state.rooms);   // kartalardagi "kimlar uchun" nomlari to'liq chiqishi uchun
}

/* ============ 8) Bino: qavatlar ro'yxati (rasm — haqiqiy surat) ============ */

const floorName = (n) => (n < 0 ? `${Math.abs(n)}-yer osti qavat (${n})` : `${n}-qavat`);

function renderFloors(h) {
  $("floorList").innerHTML = h.floors.map((f) =>
    `<li><button type="button" data-floor="${f.floor}">${f.floor < 0 ? "−" + Math.abs(f.floor) : f.floor}-qavat</button></li>`).join("");
  showFloor(1);
}

function showFloor(n) {
  const f = (state.hotel?.floors || []).find((x) => x.floor === n);
  if (!f) return;
  document.querySelectorAll("#floorList button").forEach((el) => el.classList.toggle("sel", Number(el.dataset.floor) === n));
  const types = f.room_types.length
    ? `<p class="muted small">Shu qavatdagi xona turlari (bosing):</p><div class="meta">${f.room_types.map((t) =>
        `<button type="button" class="chip chip-btn" data-room="${t.id}">${esc(t.code)} · ${esc(t.name)} · $${t.price}</button>`).join("")}</div>`
    : "";
  $("floorPanel").innerHTML = `<h3>${esc(floorName(n))}</h3><p><b>${esc(f.title)}</b></p><p class="muted">${esc(f.what)}</p>${types}`;
}

$("floorList").addEventListener("click", (e) => {
  const b = e.target.closest("[data-floor]");
  if (b) showFloor(Number(b.dataset.floor));
});
$("floorPanel").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-room]");
  if (btn) openRoom(Number(btn.dataset.room));
});

/* ============ Kutib olish, galereya, balkondan ko'rinish ============ */

function renderWelcome(h) {
  const w = h.welcome;
  $("welcomeTitle").textContent = w.title;
  $("welcomeIntro").textContent = w.intro;
  $("welcomeSteps").innerHTML = w.steps.map((s) => `
    <li><img src="${esc(s.image)}" alt="${esc(s.title)} (namunaviy surat)" width="600" height="450" loading="lazy">
      <div class="w-body"><h3><span class="w-n">${s.n}</span>${esc(s.title)}</h3><p>${esc(s.text)}</p></div></li>`).join("");
}

function renderGallery(h, group) {
  const groups = [...new Set(h.gallery.map((g) => g.group))];
  group = group || groups[0];
  $("galleryTabs").innerHTML = groups.map((g) =>
    `<button type="button" role="tab" class="${g === group ? "on" : ""}" aria-selected="${g === group}" data-group="${esc(g)}">${esc(g)}</button>`).join("");
  $("galleryGrid").innerHTML = h.gallery.filter((g) => g.group === group).map((g) =>
    `<figure class="gal-item"><img src="${esc(g.src)}" alt="${esc(g.caption)}" width="600" height="400" loading="lazy"><figcaption>${esc(g.caption)}</figcaption></figure>`).join("");
}

$("galleryTabs").addEventListener("click", (e) => {
  const b = e.target.closest("[data-group]");
  if (b && state.hotel) renderGallery(state.hotel, b.dataset.group);
});

function renderBalcony(h) {
  const b = h.balcony_view;
  $("balconySub").textContent = `Balkonli xonalar ${b.direction} tomonga qaraydi: chap tomonda teleminora, o'ng tomonda xiyobon va bog'.`;
  $("balconyImg").src = b.image;
  $("balconyList").innerHTML = [["📡", "Chap tomonda", b.left], ["🌳", "O'ng tomonda", b.right], ["ℹ️", "Eslatma", b.note]]
    .map(([ic, t, txt]) => `<li><span>${ic}</span><div><b>${esc(t)}</b><br>${esc(txt)}</div></li>`).join("");
}

function renderEntrance(h) {
  const e = h.entrance;
  $("entranceList").innerHTML = [["⛲", "Favvora", e.fountain], ["🏛️", "Kirish", e.canopy], ["🚗", "Valet", e.valet], ["💳", "Valet narxi", e.valet_price]]
    .map(([ic, t, txt]) => `<li><span>${ic}</span><div><b>${esc(t)}</b><br>${esc(txt)}</div></li>`).join("");
}

/* ============ 9) Xodimlar va valet ============ */

function renderStaff(h) {
  $("valetSteps").innerHTML = [
    ["Mashinada kelasiz", "Eshik oldiga to'xtaysiz — valet xodimi sizni kutib oladi."],
    ["Kalitni topshirasiz", "Xodim raqamli kvitansiya beradi va mashinani yer osti avtoturargohga olib boradi."],
    ["Mashina tayyor", "Ketayotganda resepshnga ayting — 3–5 daqiqada mashina eshik oldiga keltiriladi."],
  ].map(([t, d], i) => `<li><b>${i + 1}. ${esc(t)}</b><span>${esc(d)}</span></li>`).join("");
  $("staffGrid").innerHTML = h.staff.map((p) => `
    <div class="staff">
      <div class="staff-top"><span class="staff-ico">${p.icon}</span>
        <span class="swatches" title="Forma ranglari">${p.colors.map((c) => `<i style="background:${esc(c)}"></i>`).join("")}</span></div>
      <h3>${esc(p.role)}</h3>
      <p><b>Forma:</b> ${esc(p.uniform)}</p>
      <p class="muted">${esc(p.does)}</p>
    </div>`).join("");
}

/* ============ Ishga tushirish ============ */
initDates();
loadRooms(false);
api("/api/hotel").then(renderHotel).catch(() => { renderAudienceBar([]); });
api("/api/health").then((h) => {
  $("aiStatus").textContent = h.ai_enabled ? `AI faol · model: ${h.model}` : "AI zaxira rejimida (HF_TOKEN kiritilmagan)";
}).catch(() => {});
