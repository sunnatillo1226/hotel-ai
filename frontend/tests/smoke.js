// smoke.js — sayt testi: index.html + app.js ni HAQIQIY backend (config.js dagi manzil) bilan ishga tushirib tekshiradi.
// Ishga tushirish: backend ishlab turganda   npm install jsdom   va   node smoke.js
// Sanalar bugundan hisoblanadi, shuning uchun test istalgan vaqtda ishlaydi.
const { JSDOM } = require("jsdom");
const fs = require("fs");
const ROOT = require("path").join(__dirname, "..") + "/";
const iso = (n) => new Date(Date.now() + n * 86400000).toISOString().slice(0, 10);
// Har ishga tushirishda yangi email — oldingi test bronlari natijaga aralashmaydi
const EMAIL = `test${Date.now()}@mail.com`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let fails = 0;
const check = (name, ok, extra = "") => { console.log((ok ? "OK   " : "XATO ") + name + (extra ? " — " + extra : "")); if (!ok) fails++; };

(async () => {
  const html = fs.readFileSync(ROOT + "index.html", "utf8").replace(/<script src=.*?<\/script>/g, "");
  const dom = new JSDOM(html, { runScripts: "outside-only", url: "http://localhost:5500/" });
  const w = dom.window;
  w.fetch = fetch;
  w.alert = (m) => console.log("   alert:", m);
  w.confirm = () => true;
  w.HTMLElement.prototype.scrollIntoView = () => {};
  w.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
  w.HTMLDialogElement.prototype.close = function () { this.open = false; };
  const errors = [];
  w.addEventListener("error", (e) => errors.push(e.message));
  w.eval(fs.readFileSync(ROOT + "config.js", "utf8"));
  w.eval(fs.readFileSync(ROOT + "app.js", "utf8").replace(/^const /gm, "var ").replace(/^(const|let) state/gm, "var state"));
  const d = w.document;
  const $ = (id) => d.getElementById(id);

  await sleep(1200);
  check("8 xona turi yuklandi", d.querySelectorAll("#roomGrid .card").length === 8, d.querySelectorAll("#roomGrid .card").length + " ta karta");
  check("kartada m², karavot va 'Jami ... ta xona' bor", /m²/.test(d.querySelector("#roomGrid .card").textContent) && d.querySelector("#roomGrid .card").textContent.includes("Jami"));
  check("rasm tegi (lazy) bor", d.querySelectorAll("#roomGrid img.photo[loading=lazy]").length === 8);
  check("hero faktlari (84 xona)", $("heroFacts").textContent.includes("84") && $("heroFacts").textContent.includes("avtoturargoh"), $("heroFacts").textContent.slice(0, 70));
  check("bino tuzilishi / qulayliklar / hujjatlar chizildi",
    d.querySelectorAll("#layoutList li").length === 9 && d.querySelectorAll("#facilityGrid .fac").length === 8 && d.querySelectorAll("#docGrid .doc").length === 4);
  check("hujjatlarda er-xotinlar uchun nikoh guvohnomasi talabi yozilgan", /nikoh guvohnomasi/i.test($("docGrid").textContent) && !$("docGrid").textContent.includes("SO'RALMAYDI"));
  check("joylashuv: masofalar (hisoblangan) + xarita (iframe) + havola", d.querySelectorAll("#distanceList li").length === 5 && $("mapFrame").src.includes("openstreetmap.org/export/embed") && $("mapLink").href.includes("openstreetmap") && $("distanceList").textContent.includes("teleminorasi"));

  check("xodimlar va forma chizildi (7 xodim, valet bor)", d.querySelectorAll("#staffGrid .staff").length === 7 && $("staffGrid").textContent.includes("Valet haydovchi") && $("staffGrid").textContent.includes("Forma:"));
  check("valet bosqichlari (3) va kirish: favvora", d.querySelectorAll("#valetSteps li").length === 3 && $("entranceList").textContent.includes("Favvora"));
  check("bino: haqiqiy surat + 11 qavat tugmasi + panel", !!d.querySelector(".building-photo img") && d.querySelectorAll("#floorList button").length === 11 && $("floorPanel").textContent.length > 0);
  d.querySelector('#floorList [data-floor="9"]').dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  check("9-qavat bosildi: Prezident Suite", $("floorPanel").textContent.includes("Prezident"));
  check("kutib olish xizmati: 5 bosqich, har birida surat", d.querySelectorAll("#welcomeSteps li").length === 5 && d.querySelectorAll("#welcomeSteps img").length === 5);
  check("galereya: bo'limlar + suratlar", d.querySelectorAll("#galleryTabs button").length >= 7 && d.querySelectorAll("#galleryGrid img").length >= 2);
  d.querySelector('#galleryTabs [data-group="Zallar"]').dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  check("galereya: 'Zallar' tanlandi", d.querySelectorAll("#galleryGrid img").length === 2);
  check("balkondan ko'rinish: chap teleminora, o'ng xiyobon", $("balconyList").textContent.includes("Chap tomonda") && $("balconyList").textContent.includes("teleminorasi") && $("balconyImg").src.includes("balcony-view"));

  // "Kimlar uchun?" filtri
  d.querySelector('[data-aud="couple"]').dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await sleep(700);
  const coupleCards = d.querySelectorAll("#roomGrid .card").length;
  check("juftliklar uchun filtr", coupleCards === 4 && !$("audienceHint").hidden, coupleCards + " ta xona (kutilgan 4)");
  d.querySelector('[data-aud=""]').dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await sleep(700);
  check("filtr tozalandi", d.querySelectorAll("#roomGrid .card").length === 8);
  check("AI holati yozildi", $("aiStatus").textContent.length > 0, $("aiStatus").textContent);

  // oddiy qidiruv
  $("fGuests").value = "4";
  $("searchForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(800);
  const cards = d.querySelectorAll("#roomGrid .card").length;
  check("4 kishilik qidiruv", cards === 2, cards + " ta xona (kutilgan 2)");
  check("Bo'sh/Band belgisi bor", d.querySelectorAll(".badge.ok").length === cards);

  // AI qidiruv
  $("aiText").value = "Oilam bilan 4 kishi, balkonli xona kerak, 160$ gacha";
  $("aiForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(1000);
  check("AI qidiruv filtr ko'rsatdi", !$("aiFilters").hidden && $("aiFilters").textContent.includes("160"), $("aiFilters").textContent.slice(0, 90));
  check("AI birinchi xona: Family xona", d.querySelector("#roomGrid .card h3").textContent === "Family xona", d.querySelector("#roomGrid .card h3")?.textContent);

  // xona oynasi + bron
  d.querySelector("#roomGrid .card").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await sleep(600);
  check("xona oynasi ochildi", $("roomDialog").open === true && !!$("bookForm"));
  const f = $("bookForm");
  f.elements.guest_name.value = "Test Foydalanuvchi"; f.elements.guest_email.value = EMAIL; f.elements.guests.value = "4";
  f.elements.check_in.value = iso(40); f.elements.check_out.value = iso(43);
  f.elements.check_in.dispatchEvent(new w.Event("change"));
  check("jami narx hisoblandi (130$ x 3)", $("totalInfo").textContent === "Jami: $390", $("totalInfo").textContent);
  check("xona oynasida ko'p surat (miniatyuralar)", d.querySelectorAll("#dlgThumbs button").length >= 3);
  d.querySelectorAll("#dlgThumbs button")[1].dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  check("miniatyura bosilganda asosiy surat almashdi", d.querySelector("#dlgBody .dlg-banner .photo").src.includes("img/") && $("dlgCap").textContent.length > 0, $("dlgCap").textContent);
  check("oynada hujjat maydonlari va nikoh talabi bor", !!f.elements.doc_type && !!f.elements.doc_number && $("dlgBody").textContent.includes("nikoh guvohnomasi"));
  // hujjatsiz — brauzer tekshiruvi; backend ham rad etadi (pytest da tekshirilgan). Bu yerda to'g'ri to'ldiramiz.
  f.elements.doc_type.value = "passport"; f.elements.doc_number.value = "AB1234567";
  check("er-xotin belgisi: guvohnoma maydoni ochiladi", $("certWrap").hidden === true);
  f.elements.is_couple.checked = true; f.elements.is_couple.dispatchEvent(new w.Event("change"));
  check("belgilanganda guvohnoma maydoni ko'rindi va majburiy", $("certWrap").hidden === false && f.elements.marriage_cert_number.required === true);
  f.elements.marriage_cert_number.value = "";
  f.dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  check("guvohnomasiz juftlik rad etildi (backend)", $("bookMsg").className.includes("err") && $("bookMsg").textContent.includes("nikoh guvohnomasi"), $("bookMsg").textContent.slice(0, 80));
  f.elements.marriage_cert_number.value = "II-123456";
  f.dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  check("bron tasdiqlandi", $("bookMsg").className.includes("good"), $("bookMsg").textContent.slice(0, 60));

  // sharh
  const rf = $("reviewForm");
  rf.elements.author.value = "Sharhchi"; rf.elements.rating.value = "5"; rf.elements.comment.value = "Juda toza va qulay, rahmat!";
  rf.dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  check("sharh + AI kayfiyat", $("revMsg").textContent.includes("Ijobiy"), $("revMsg").textContent);
  $("roomDialog").close();

  // zaxira: bron qilingach shu sanalarda 8 ta Family xonadan 7 tasi qoladi
  const stockOf = () => [...d.querySelectorAll("#roomGrid .card")].find((c) => c.querySelector("h3").textContent === "Family xona")?.textContent || "";
  $("fCheckIn").value = iso(40); $("fCheckOut").value = iso(43); $("fGuests").value = "4";
  $("searchForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(800);
  check("bron qilingach 'Qolgan: 7 xona'", stockOf().includes("Qolgan: 7 xona"), (stockOf().match(/Qolgan: \d+ xona/) || ["yo'q"])[0]);

  // mening bronlarim + bekor
  $("myEmail").value = EMAIL;
  $("myForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(700);
  check("mening bronlarim ko'rsatildi", d.querySelectorAll("#myList .booking").length === 1);
  d.querySelector("[data-cancel]").dispatchEvent(new w.MouseEvent("click", { bubbles: true }));
  await sleep(900);
  check("bron bekor qilindi", d.querySelector("#myList .booking.cancelled") !== null);
  $("searchForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(800);
  check("bekordan keyin 'Qolgan: 8 xona'", stockOf().includes("Qolgan: 8 xona"));

  // chat
  $("chatFab").click();
  $("chatInput").value = "Nonushta bormi?";
  $("chatForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  $("chatInput").value = "Mashina qo'yadigan joy bormi?";
  $("chatForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  const bubbles = [...d.querySelectorAll(".bubble")].map((b) => b.textContent);
  check("chat: nonushta", bubbles.some((t) => t.includes("07:00")));
  $("chatInput").value = "Valet xizmati qanday?";
  $("chatForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  check("chat: valet", [...d.querySelectorAll(".bubble")].some((b) => b.textContent.includes("olib keladi")));
  check("chat: avtoturargoh", bubbles.some((t) => t.includes("BEPUL")));
  $("chatInput").value = "Kutib olish xizmati qanday?";
  $("chatForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  check("chat: kutib olish xizmati", [...d.querySelectorAll(".bubble")].some((b) => b.textContent.includes("bellboy")));
  check("chat: keyingi savol tugmalari", d.querySelectorAll("#chatQuick button").length >= 1 && d.querySelectorAll("#chatQuick button").length <= 3);
  $("chatQuick").querySelector("button").click();                     // taklif tugmasi bosiladi -> yangi savol yuboriladi
  await sleep(900);
  check("chat: taklif tugmasi ishlaydi", d.querySelectorAll(".bubble.me").length === 5);
  $("chatInput").value = "Aeroportdan transfer bormi?";
  $("chatForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  check("chat: transfer = aeroport (15$)", [...d.querySelectorAll(".bubble.bot")].pop().textContent.includes("15$"));

  $("chatInput").value = "Lobby suratlarini ko'rsating";
  $("chatForm").dispatchEvent(new w.Event("submit", { cancelable: true }));
  await sleep(900);
  check("chat: rasm savoliga suratlar chatda chiqdi", d.querySelectorAll(".bubble.bot .chat-photos img").length >= 2);

  check("JS xatolari yo'q", errors.length === 0, errors.join("; "));
  console.log(fails ? `\n${fails} ta xato` : "\nHammasi yaxshi");
  process.exit(fails ? 1 : 0);
})();
