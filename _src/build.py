"""Build the language pages of carhunterworld.com from one template.

Run from the repo root:  python _src/build.py
Writes index.html (en), ru/index.html, ka/index.html, fa/index.html. Edit texts here, never in
the generated files. _src/ is not published: Jekyll on GitHub Pages skips folders that start
with "_". Legal pages (privacy/terms/data-deletion) stay English-only and are not generated.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICONS = Path(__file__).resolve().parent / "icons"
SITE = "https://carhunterworld.com"
# One tag for the whole site, so `prod_stats.py sources` shows it as one placement.
BOT_URL = "https://t.me/CarHunterGE_bot?start=src_site"

LANGS = [("en", "English", "/"), ("ru", "Русский", "/ru/"), ("ka", "ქართული", "/ka/"), ("fa", "فارسی", "/fa/")]
FONTS = {
    "en": "family=Inter:wght@400;600;700;800",
    "ru": "family=Inter:wght@400;600;700;800",
    "ka": "family=Noto+Sans+Georgian:wght@400;600;700;800&family=Inter:wght@400;700;800",
    "fa": "family=Vazirmatn:wght@400;600;700;800&family=Inter:wght@400;700;800",
}

# Real deal from the content queue (myauto-123704814, approved for posting 2026-10-16).
# Numbers must come from the feed, never invented (memory: no-invented-numbers-in-drafts).
DEAL = {"hot": "WOW -27%", "model": "Audi Q5 2016", "engine": "2.0L turbo",
        "km": "189 000", "price": "$8 000", "market": "~$11 000", "time": "09:41"}

T = {
    "en": {
        "title": "CarHunter World: cars under market price",
        "desc": "A Telegram bot that finds cars under market price every day. Set a filter and get the best deals in your chat.",
        "eyebrow": "Telegram bot for car buyers",
        "h1": "Cars under market price.", "h1_accent": "Every day.",
        "lead": "CarHunter checks car listings all day and compares every price with the market. "
                "When a car costs much less than similar cars, you get a message first.",
        "cta": "Open the bot in Telegram", "cta2": "How it works",
        "chips": ["Free trial", "No card needed", "Works in Telegram"],
        "note": "Now working in Georgia.",
        "card": {"km": "km", "market": "market", "place": "Tbilisi"},
        "caption": "Real example from the bot, 16 October",
        "how_title": "How it works", "how_sub": "Three steps. One minute to start.",
        "steps": [
            ("Set a filter", "Choose your budget, make and car age. Choose how far below market the price must be."),
            ("Get deals first", "The bot sends you cars that cost less than similar cars. You see them first."),
            ("Check the VIN", "Send a VIN and see if the car came from a US auction."),
        ],
        "trust_title": "Why you can trust the price",
        "trust": [
            ("Same model, same year", "We compare each car only with similar cars."),
            ("Real listings", "Prices come from public car sites and update all day."),
            ("Clear numbers", "Every deal shows the market price, so you can check it."),
        ],
        "final_title": "Ready to find your car?",
        "final_sub": "Set a filter in one minute. The bot does the rest.",
        "follow": "Follow CarHunter World", "tg_channel": "Telegram channel",
        "questions": "Questions? Write to",
        "legal": ["Privacy Policy", "Terms of Service", "Data deletion"], "legal_suffix": "",
    },
    "ru": {
        "title": "CarHunter World: авто дешевле рынка",
        "desc": "Telegram-бот, который каждый день находит авто дешевле рынка. Настрой фильтр и получай лучшие предложения в чат.",
        "eyebrow": "Telegram-бот для покупателей авто",
        "h1": "Авто дешевле рынка.", "h1_accent": "Каждый день.",
        "lead": "CarHunter весь день смотрит объявления и сравнивает каждую цену с рынком. "
                "Когда машина стоит намного дешевле похожих, ты первым получаешь сообщение.",
        "cta": "Открыть бота в Telegram", "cta2": "Как это работает",
        "chips": ["Бесплатный пробный период", "Без карты", "Работает в Telegram"],
        "note": "Сейчас работаем в Грузии.",
        "card": {"km": "км", "market": "рынок", "place": "Тбилиси"},
        "caption": "Реальный пример из бота, 16 октября",
        "how_title": "Как это работает", "how_sub": "Три шага. Минута на старт.",
        "steps": [
            ("Настрой фильтр", "Выбери бюджет, марку и возраст авто. Укажи, насколько цена должна быть ниже рынка."),
            ("Получай сделки первым", "Бот присылает машины, которые стоят меньше похожих. Ты видишь их первым."),
            ("Проверь VIN", "Отправь VIN и узнай, не с американского ли аукциона машина."),
        ],
        "trust_title": "Почему цене можно верить",
        "trust": [
            ("Та же модель, тот же год", "Каждую машину сравниваем только с похожими."),
            ("Живые объявления", "Цены берём с открытых авто-сайтов, они обновляются весь день."),
            ("Понятные цифры", "В каждой сделке видна цена рынка, её легко проверить."),
        ],
        "final_title": "Готов найти свою машину?",
        "final_sub": "Фильтр настраивается за минуту. Остальное сделает бот.",
        "follow": "Подписывайся на CarHunter World", "tg_channel": "Telegram-канал",
        "questions": "Вопросы? Пиши на",
        "legal": ["Политика конфиденциальности", "Условия использования", "Удаление данных"],
        "legal_suffix": " (EN)",
    },
    "ka": {
        "title": "CarHunter World: მანქანები ბაზარზე იაფად",
        "desc": "Telegram-ბოტი, რომელიც ყოველდღე პოულობს ბაზარზე იაფ მანქანებს. დააყენე ფილტრი და მიიღე საუკეთესო შეთავაზებები ჩატში.",
        "eyebrow": "Telegram-ბოტი მანქანის მყიდველებისთვის",
        "h1": "მანქანები ბაზარზე იაფად.", "h1_accent": "ყოველდღე.",
        "lead": "CarHunter მთელი დღე ამოწმებს განცხადებებს და თითოეულ ფასს ბაზარს ადარებს. "
                "როცა მანქანა მსგავსებზე ბევრად იაფია, შეტყობინებას პირველი მიიღებ.",
        "cta": "გახსენი ბოტი Telegram-ში", "cta2": "როგორ მუშაობს",
        "chips": ["უფასო საცდელი პერიოდი", "ბარათის გარეშე", "მუშაობს Telegram-ში"],
        "note": "ახლა ვმუშაობთ საქართველოში.",
        "card": {"km": "კმ", "market": "ბაზარი", "place": "თბილისი"},
        "caption": "რეალური მაგალითი ბოტიდან, 16 ოქტომბერი",
        "how_title": "როგორ მუშაობს", "how_sub": "სამი ნაბიჯი. დაწყებას ერთი წუთი სჭირდება.",
        "steps": [
            ("დააყენე ფილტრი", "აირჩიე ბიუჯეტი, მარკა და მანქანის ასაკი. მიუთითე, რამდენით დაბალი უნდა იყოს ფასი ბაზარზე."),
            ("მიიღე შეთავაზებები პირველმა", "ბოტი გიგზავნის მანქანებს, რომლებიც მსგავსებზე იაფია. მათ პირველი ნახავ."),
            ("შეამოწმე VIN", "გამოგზავნე VIN და გაიგე, ხომ არ არის მანქანა ამერიკული აუქციონიდან."),
        ],
        "trust_title": "რატომ არის ფასი სანდო",
        "trust": [
            ("იგივე მოდელი, იგივე წელი", "თითოეულ მანქანას მხოლოდ მსგავს მანქანებს ვადარებთ."),
            ("რეალური განცხადებები", "ფასები ღია ავტო-საიტებიდანაა და მთელი დღე ახლდება."),
            ("გასაგები ციფრები", "ყველა შეთავაზებაში ჩანს ბაზრის ფასი, ასე რომ, მარტივად შეამოწმებ."),
        ],
        "final_title": "მზად ხარ, იპოვო შენი მანქანა?",
        "final_sub": "ფილტრი ერთ წუთში ყენდება. დანარჩენს ბოტი გააკეთებს.",
        "follow": "გამოიწერე CarHunter World", "tg_channel": "Telegram-არხი",
        "questions": "კითხვები გაქვს? მოგვწერე:",
        "legal": ["კონფიდენციალურობის პოლიტიკა", "გამოყენების პირობები", "მონაცემების წაშლა"],
        "legal_suffix": " (EN)",
    },
    "fa": {
        "title": "CarHunter World: خودرو زیر قیمت بازار",
        "desc": "ربات تلگرامی که هر روز خودروهای زیر قیمت بازار را پیدا می‌کند. فیلتر بگذار و بهترین پیشنهادها را در چت بگیر.",
        "eyebrow": "ربات تلگرام برای خریداران خودرو",
        "h1": "خودرو زیر قیمت بازار.", "h1_accent": "هر روز.",
        "lead": "CarHunter تمام روز آگهی‌ها را بررسی می‌کند و هر قیمت را با بازار مقایسه می‌کند. "
                "وقتی خودرویی خیلی ارزان‌تر از خودروهای مشابه باشد، اول از همه به تو پیام می‌دهد.",
        "cta": "باز کردن ربات در تلگرام", "cta2": "چطور کار می‌کند",
        "chips": ["دوره‌ی آزمایشی رایگان", "بدون کارت", "داخل تلگرام"],
        "note": "فعلاً در گرجستان فعال هستیم.",
        # The bot card itself is Georgian/English, so the mock stays in English here.
        "card": {"km": "km", "market": "market", "place": "Tbilisi"},
        "caption": "نمونه‌ی واقعی از ربات، ۱۶ اکتبر",
        "how_title": "چطور کار می‌کند", "how_sub": "سه قدم. شروع فقط یک دقیقه طول می‌کشد.",
        "steps": [
            ("فیلتر بگذار", "بودجه، برند و عمر خودرو را انتخاب کن. بگو قیمت چقدر باید زیر بازار باشد."),
            ("پیشنهادها را زودتر بگیر", "ربات خودروهایی را می‌فرستد که از خودروهای مشابه ارزان‌ترند. تو اول از همه آن‌ها را می‌بینی."),
            ("VIN را بررسی کن", "VIN را بفرست و ببین خودرو از حراجی آمریکا آمده یا نه."),
        ],
        "trust_title": "چرا می‌توانی به قیمت اعتماد کنی",
        "trust": [
            ("همان مدل، همان سال", "هر خودرو را فقط با خودروهای مشابه مقایسه می‌کنیم."),
            ("آگهی‌های واقعی", "قیمت‌ها از سایت‌های عمومی خودرو می‌آیند و تمام روز به‌روز می‌شوند."),
            ("اعداد روشن", "در هر پیشنهاد قیمت بازار را می‌بینی و راحت می‌توانی بررسی کنی."),
        ],
        "final_title": "آماده‌ای خودروی خودت را پیدا کنی؟",
        "final_sub": "فیلتر در یک دقیقه تنظیم می‌شود. بقیه‌اش با ربات.",
        "follow": "CarHunter World را دنبال کن", "tg_channel": "کانال تلگرام",
        "questions": "سؤالی داری؟ بنویس به",
        "legal": ["سیاست حریم خصوصی", "شرایط استفاده", "حذف داده‌ها"],
        "legal_suffix": " (EN)",
    },
}

SOCIAL = [
    ("instagram", "Instagram", "https://www.instagram.com/carhunterworld/"),
    ("facebook", "Facebook", "https://www.facebook.com/carhunterworld"),
    ("tiktok", "TikTok", "https://www.tiktok.com/@carhunterworld"),
    ("telegram", None, "https://t.me/carhunterworld"),
]

# Feather-style line icons, drawn with currentColor.
_LINE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>'
LINE_ICONS = {
    "sliders": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/>'
               '<line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/>'
               '<line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    "bell": '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "refresh": '<polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>'
               '<path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>',
    "chart": '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
}
CROSSHAIR = ('<svg class="crosshair" viewBox="0 0 200 200" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
             '<circle cx="100" cy="100" r="80"/><circle cx="100" cy="100" r="40"/><circle cx="100" cy="100" r="4" fill="currentColor"/>'
             '<line x1="100" y1="0" x2="100" y2="60"/><line x1="100" y1="140" x2="100" y2="200"/>'
             '<line x1="0" y1="100" x2="60" y2="100"/><line x1="140" y1="100" x2="200" y2="100"/></svg>')


def line_icon(name: str) -> str:
    return _LINE.format(LINE_ICONS[name])


def brand_icon(name: str) -> str:
    # simple-icons SVGs: drop the <title> (the link text names the network) and hide from AT.
    svg = (ICONS / f"{name}.svg").read_text(encoding="utf-8").strip()
    svg = svg.replace('role="img"', 'aria-hidden="true"')
    start, end = svg.find("<title>"), svg.find("</title>")
    if start != -1:
        svg = svg[:start] + svg[end + len("</title>"):]
    return svg


def page(lang: str) -> str:
    t = T[lang]
    e = escape
    path = dict((code, url) for code, _, url in LANGS)[lang]
    rtl = ' dir="rtl"' if lang == "fa" else ""
    auto = ' data-autolang="1"' if lang == "en" else ""
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{code}" href="{SITE}{url}">' for code, _, url in LANGS
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/">'
    langs = "".join(
        f'<a href="{url}" data-lang="{code}" lang="{code}"'
        + (' aria-current="page"' if code == lang else "")
        + f'><span class="full">{e(name)}</span><span class="short">{code.upper()}</span></a>'
        for code, name, url in LANGS
    )
    chips = "".join(f"<li>{line_icon('check')}{e(c)}</li>" for c in t["chips"])
    c = t["card"]
    steps = "".join(
        f'<div class="card"><span class="step-no">0{i}</span><div class="icon">{line_icon(icon)}</div>'
        f"<h3>{e(h)}</h3><p>{e(p)}</p></div>"
        for i, ((h, p), icon) in enumerate(zip(t["steps"], ["sliders", "bell", "shield"]), start=1)
    )
    trust = "".join(
        f'<div><span class="icon">{line_icon(icon)}</span><span><h3>{e(h)}</h3><p>{e(p)}</p></span></div>'
        for (h, p), icon in zip(t["trust"], ["target", "refresh", "chart"])
    )
    social = "".join(
        f'<a href="{url}">{brand_icon(key)}{e(label or t["tg_channel"])}</a>' for key, label, url in SOCIAL
    )
    legal = "".join(
        f'<li><a href="/{href}">{e(name)}{e(t["legal_suffix"])}</a></li>'
        for href, name in zip(["privacy.html", "terms.html", "data-deletion.html"], t["legal"])
    )
    tg = brand_icon("telegram")
    return f"""<!doctype html>
<html lang="{lang}"{rtl}{auto}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t["title"])}</title>
<meta name="description" content="{e(t["desc"])}">
<link rel="canonical" href="{SITE}{path}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:title" content="{e(t["title"])}">
<meta property="og:description" content="{e(t["desc"])}">
<meta property="og:image" content="{SITE}/logo.png">
<link rel="icon" type="image/png" href="/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{FONTS[lang]}&display=swap">
<link rel="stylesheet" href="/style.css">
<script src="/lang.js"></script>
</head>
<body>

<header class="hero">
  {CROSSHAIR}
  <div class="wrap">
    <nav class="nav">
      <a class="brand" href="{path}"><img src="/logo.png" alt="">CarHunter World</a>
      <div class="langs">{langs}</div>
    </nav>
    <div class="hero-grid">
      <div>
        <span class="eyebrow">{e(t["eyebrow"])}</span>
        <h1>{e(t["h1"])} <span>{e(t["h1_accent"])}</span></h1>
        <p class="lead">{e(t["lead"])}</p>
        <div class="actions">
          <a class="btn btn-gold" href="{BOT_URL}">{tg}{e(t["cta"])}</a>
          <a class="btn btn-ghost" href="#how">{e(t["cta2"])}</a>
        </div>
        <ul class="chips">{chips}</ul>
        <p class="note">{e(t["note"])}</p>
      </div>
      <div class="phone-col">
        <div class="phone" aria-hidden="true">
          <div class="phone-top"><img src="/logo.png" alt=""><div><b>CarHunterGE</b><small>bot</small></div></div>
          <div class="bubble">
            <div class="hot">🎯 {DEAL["hot"]}</div>
            <div class="model">{DEAL["model"]}</div>
            <div>⛽ {DEAL["engine"]}</div>
            <div>🛣 {DEAL["km"]} {e(c["km"])}</div>
            <div>💰 {DEAL["price"]}</div>
            <div class="market">{e(c["market"])} {DEAL["market"]}</div>
            <div>📍 {e(c["place"])}</div>
            <time>{DEAL["time"]}</time>
          </div>
        </div>
        <div class="caption">{e(t["caption"])}</div>
      </div>
    </div>
  </div>
</header>

<main class="wrap">
  <section id="how">
    <div class="section-head"><h2>{e(t["how_title"])}</h2><p>{e(t["how_sub"])}</p></div>
    <div class="cards">{steps}</div>
  </section>

  <section>
    <div class="section-head"><h2>{e(t["trust_title"])}</h2></div>
    <div class="trust">{trust}</div>
  </section>

  <div class="final">
    <h2>{e(t["final_title"])}</h2>
    <p>{e(t["final_sub"])}</p>
    <a class="btn btn-gold" href="{BOT_URL}">{tg}{e(t["cta"])}</a>
  </div>

  <section>
    <div class="section-head"><h2>{e(t["follow"])}</h2></div>
    <div class="social">{social}</div>
  </section>

  <footer>
    {e(t["questions"])} <a href="mailto:hello@carhunterworld.com">hello@carhunterworld.com</a>
    <ul>{legal}</ul>
  </footer>
</main>

</body>
</html>
"""


def main() -> None:
    for code, _, url in LANGS:
        out = ROOT / url.strip("/") / "index.html" if url != "/" else ROOT / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(code), encoding="utf-8", newline="\n")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
