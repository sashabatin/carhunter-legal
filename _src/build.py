"""Build the language pages of carhunterworld.com from one template.

Run from the repo root:  python _src/build.py
Writes index.html (en), ru/index.html, ka/index.html, fa/index.html. Edit texts here, never in
the generated files. _src/ is not published: Jekyll on GitHub Pages skips folders that start
with "_". Legal pages (privacy/terms/data-deletion) stay English-only and are not generated.

Design: direction B "price on the windshield", agreed 17.10 on the Claude Design board
(Windshield.dc.html, v11). The three deals come from _src/deals.json (python _src/pick_deals.py).
"""
import json
import sys
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://carhunterworld.com"
BOT = "https://t.me/CarHunterGE_bot"
# One tag for the whole site, so `prod_stats.py sources` shows it as one placement.
SRC = "site"
# Plan buttons go straight to the Tribute checkout (owner, 18.10: every step before paying loses
# buyers). Same links as prod env TRIBUTE_LINK_FAST / TRIBUTE_LINK / TRIBUTE_LINK_PRO, checked
# 18.10; when one changes there, change it here. Only the t.me/tribute/app form, never a web link.
TRIBUTE = {"fast": "https://t.me/tribute/app?startapp=s12F9",
           "vip": "https://t.me/tribute/app?startapp=s108W",
           "pro": "https://t.me/tribute/app?startapp=s12DN"}

# The bot's numbers, in ONE place: change them here when the bot env changes.
TRIAL_DAYS = 21          # bot env TRIAL_DAYS
TRIAL_VIN = 10           # bot env VIN_QUOTA_TRIAL
# (id, shown name, EUR, period, VIN checks per period, filters, garage, struck-out old EUR);
# None = unlimited, or no old price. Yearly periods were removed in Tribute 21.10 (Tribute
# preselected the year). VIP promo 21.10: EUR 14 instead of 19 and 30 checks, open until
# Dec 31 (the "promo" strings); Tribute support confirmed subscribers keep their price.
PLANS = [("fast", "Fast", 6, "week", 10, 10, 10, None),
         ("vip", "VIP", 14, "month", 30, 15, 15, 19),
         ("pro", "PRO", 49, "month", 120, None, None, None)]
# Fast renews weekly: 6 x 30/7 = 25.7. Shown so VIP reads as the cheaper way to stay (owner).
FAST_MONTH_EUR = 26


# A lot opens the bot on that car (?start=src_site__deal_<id>). Only after the bot that cuts
# the __deal_ tail is in prod: the bot before it stores "site__deal_..." as the user's source.
DEAL_LINKS_LIVE = True
# Click beacons (bot repo, function_app/site_funnel.py): counts per button, plan and ?src= tag.
# A plan button goes straight to Tribute, so this is the only trace of a sale from the site.
CLICK_API = {"prod": "https://func-carcheckerge-prod-35417.azurewebsites.net/api/site-click",
             "dev": "https://func-carcheckerge-dev-35417.azurewebsites.net/api/site-click"}


def bot_url(deal: str | None = None) -> str:
    tail = f"__deal_{deal}" if deal and DEAL_LINKS_LIVE else ""
    return f"{BOT}?start=src_{SRC}{tail}"


LANGS = [("en", "English", "/"), ("ru", "Русский", "/ru/"), ("ka", "ქართული", "/ka/"), ("fa", "فارسی", "/fa/")]
_LATIN = ("family=Fira+Sans:wght@400;500;600;700&family=Fira+Sans+Extra+Condensed:wght@600;700;800;900"
          "&family=Permanent+Marker")
FONTS = {
    "en": _LATIN,
    "ru": _LATIN,
    # Fira has no Georgian or Persian; these carry the script, Fira keeps prices and Latin words.
    "ka": _LATIN + "&family=Noto+Sans+Georgian:wdth,wght@62.5..100,400..900",
    "fa": _LATIN + "&family=Vazirmatn:wght@400;500;700;800;900",
}

_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def num(lang: str, n) -> str:
    """A number inside running text. Prices on the glass stay Latin digits in every language."""
    return str(n).translate(_FA_DIGITS) if lang == "fa" else str(n)


def ru_plural(n, one: str, few: str, many: str) -> str:
    n = int(n)   # texts get numbers already formatted by num()
    if n % 10 == 1 and n % 100 != 11:
        return one
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return few
    return many


def usd(n: int) -> str:
    return "$" + f"{n:,}".replace(",", " ")


MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
           "October", "November", "December"],
    "ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября",
           "октября", "ноября", "декабря"],
    "ka": ["იანვარი", "თებერვალი", "მარტი", "აპრილი", "მაისი", "ივნისი", "ივლისი", "აგვისტო",
           "სექტემბერი", "ოქტომბერი", "ნოემბერი", "დეკემბერი"],
    "fa": ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن", "ژوئیه", "اوت", "سپتامبر", "اکتبر",
           "نوامبر", "دسامبر"],
}
SHORT_MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "ru": ["янв", "фев", "мар", "апр", "мая", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"],
    "ka": ["იან", "თებ", "მარ", "აპრ", "მაი", "ივნ", "ივლ", "აგვ", "სექ", "ოქტ", "ნოე", "დეკ"],
    "fa": MONTHS["fa"],
}


def date_range(lang: str, a: date, b: date) -> str:
    m1, m2 = MONTHS[lang][a.month - 1], MONTHS[lang][b.month - 1]
    d1, d2, y = num(lang, a.day), num(lang, b.day), num(lang, b.year)
    if lang == "en":
        return f"{d1} to {d2} {m2} {y}" if a.month == b.month else f"{d1} {m1} to {d2} {m2} {y}"
    if lang == "ru":
        return f"с {d1} по {d2} {m2} {y}" if a.month == b.month else f"с {d1} {m1} по {d2} {m2} {y}"
    if lang == "ka":
        return f"{d1}–{d2} {m2}, {y}" if a.month == b.month else f"{d1} {m1} – {d2} {m2}, {y}"
    return f"{d1} تا {d2} {m2} {y}" if a.month == b.month else f"{d1} {m1} تا {d2} {m2} {y}"


def short_date(lang: str, d: date) -> str:
    return f"{num(lang, d.day)} {SHORT_MONTHS[lang][d.month - 1]}"


# Feed locations are English; the common ones get their own spelling, the rest stay as they are.
CITIES = {
    "Tbilisi": {"ru": "Тбилиси", "ka": "თბილისი", "fa": "تفلیس"},
    "Kutaisi": {"ru": "Кутаиси", "ka": "ქუთაისი", "fa": "کوتائیسی"},
    "Batumi": {"ru": "Батуми", "ka": "ბათუმი", "fa": "باتومی"},
    "Rustavi": {"ru": "Рустави", "ka": "რუსთავი", "fa": "روستاوی"},
    "Zugdidi": {"ru": "Зугдиди", "ka": "ზუგდიდი", "fa": "زوگدیدی"},
    "Gori": {"ru": "Гори", "ka": "გორი", "fa": "گوری"},
    "Telavi": {"ru": "Телави", "ka": "თელავი", "fa": "تلاوی"},
    "Poti": {"ru": "Поти", "ka": "ფოთი", "fa": "پوتی"},
}

T = {
    "en": {
        "title": "CarHunter World: cars under market price",
        "desc": "A Telegram bot that finds cars under market price every day. Set a filter and get the best deals in your chat.",
        "h1": "Cars under market price.", "h1_accent": "Every day.",
        "lead": "CarHunter checks car listings all day. When a car costs much less than similar cars, "
                "you get a Telegram message first.",
        "sticker_days": lambda d: f"{d} days", "sticker_free": "free",
        "sticker_note": lambda v: f"No card. Deals, VIP channel, {v} VIN checks.",
        "cta": "Open the bot in Telegram",
        "nav_label": "On this page", "lang_label": "Language",
        "nav": ["How it works", "Plans and payment", "Contacts and socials"],
        "top_h": "Top 3 deals this week",
        "top_sub": lambda r: f"The biggest discounts among real deals the bot sent, {r}. Tap a car to see it big.",
        "under": "under market", "market": "market", "km": "km",
        "strip_l": "Get deals like this first", "strip_r": "Open the bot",
        "lot_aria": lambda c: f"{c}: get deals like this first in Telegram",
        "thumb_aria": lambda c: f"Show {c} big", "photo_alt": lambda c: f"{c}, photo from the listing",
        "how_h": "How it works",
        "steps": [
            ("Set a filter", "Two questions: how far below market, and your budget. Make, age and mileage are optional."),
            ("Get deals first", "Cheap cars come to your Telegram messages. Each one shows the market price, so you can check it."),
            ("Check the VIN", "Send the VIN or a photo of the VIN plate. You see the US auction history: salvage title and accidents."),
        ],
        "plans_h": "Plans and payment",
        "trial_h": "Not ready to pay?",
        "trial_sub": "Free and no card. When it ends, it just stops: nothing is charged.",
        "trial_items": lambda v: ["Deals in your messages", "VIP channel", f"{v} VIN checks in total"],
        "trial_go": "Start free",
        "plans_note": lambda w, m1, m2: f"Paid plans run until you cancel. VIN checks renew every period: {w} a week on Fast, {m1} or {m2} a month on VIP and PRO.",
        "period": {"week": "/ 7 days", "month": "/ month"},
        "feat": {
            "fast": lambda n, f, g: ["Deals in your messages", "VIP channel", f"{n} VIN checks", f"{f} filters, {g} cars in garage"],
            "vip": lambda n, f, g: ["Everything in Fast", f"{n} VIN checks", f"{f} filters, {g} cars in garage", "Priority alerts"],
            "pro": lambda n, f, g: ["Everything in VIP", f"{n} VIN checks", "Unlimited filters and garage", "Alerts first"],
        },
        "get": lambda p: f"Get {p}",
        "recommended": "Recommended",
        "per_month": lambda m: f"≈ €{m} / month*",
        "promo": lambda p: f"Promo until Dec 31. Your €{p} stays while you are subscribed.",
        "footnote": lambda m: f"* Fast renews every week: €6 × 4.3 weeks ≈ €{m} a month.",
        "tag": {"fast": ("Need a car urgently", "A week of full access while you buy right now."),
                "vip": ("No rush, no overpaying", "Search calmly: deals come to you every day."),
                "pro": ("For resellers and dealers", "You buy to resell: the most checks, alerts before everyone.")},
        "guide_h": "How to pay and start",
        "guide": ["Tap a plan and pay in Tribute.",
                  "After payment, Tribute gives you access to the VIP channel.",
                  "Open the bot, tap START and set a filter. Then personal deals come to your messages."],
        "guide_go": "Open the bot",
        "fee": "Prices are without Tribute's service fee. Tribute adds it at checkout, and you see it before you confirm.",
        "pay_h": "How the payment works",
        "pay": [
            ("The bot never sees your card.", "The pay button opens Tribute's payment page. You enter the card there, and it never reaches us."),
            ("We store nothing about payment.", "We keep your Telegram id, your plan, its end date and your filters. No card number to leak."),
            ("Who takes the money.", "TRBT Limited (Cyprus, HE 443898), the company behind Tribute. This name shows on your bank statement."),
            ("No card? Fine.", "Besides a card, Tribute offers other ways to pay. The set depends on your device and country, and you see the full list before you pay."),
            ("There is a service fee.", "Tribute adds its own fee on top of the plan price. You see the full sum at checkout, before you confirm."),
            ("Cancel in one place.", "You manage and cancel the plan inside Tribute."),
        ],
        "contacts_h": "Contacts and socials", "questions": "Questions? Write to",
        "tg_channel": "Telegram channel",
        "legal": ["Privacy Policy", "Terms of Service", "Data deletion"], "legal_suffix": "",
    },
    "ru": {
        "title": "CarHunter World: авто дешевле рынка",
        "desc": "Telegram-бот, который каждый день находит авто дешевле рынка. Настрой фильтр и получай лучшие предложения в чат.",
        "h1": "Авто дешевле рынка.", "h1_accent": "Каждый день.",
        "lead": "CarHunter весь день смотрит объявления. Когда машина стоит намного дешевле похожих, "
                "ты первым получаешь сообщение в Telegram.",
        "sticker_days": lambda d: f"{d} {ru_plural(d, 'день', 'дня', 'дней')}", "sticker_free": "бесплатно",
        "sticker_note": lambda v: f"Без карты. Сделки, VIP\u2011канал, {v} {ru_plural(v, 'проверка', 'проверки', 'проверок')} VIN.",
        "cta": "Открыть бота в Telegram",
        "nav_label": "На этой странице", "lang_label": "Язык",
        "nav": ["Как это работает", "Тарифы и оплата", "Контакты и соцсети"],
        "top_h": "Топ-3 сделки недели",
        "top_sub": lambda r: f"Самые большие скидки среди реальных сделок, которые прислал бот, {r}. Нажми на машину, чтобы увеличить.",
        "under": "ниже рынка", "market": "рынок", "km": "км",
        "strip_l": "Получай такие сделки первым", "strip_r": "Открыть бота",
        "lot_aria": lambda c: f"{c}: получай такие сделки первым в Telegram",
        "thumb_aria": lambda c: f"Показать {c} крупно", "photo_alt": lambda c: f"{c}, фото из объявления",
        "how_h": "Как это работает",
        "steps": [
            ("Настрой фильтр", "Два вопроса: насколько ниже рынка и какой бюджет. Марка, возраст и пробег по желанию."),
            ("Получай сделки первым", "Дешёвые машины приходят тебе в Telegram. У каждой видна цена рынка, её легко проверить."),
            ("Проверь VIN", "Отправь VIN или фото таблички с VIN. Увидишь историю с аукционов США: salvage и ДТП."),
        ],
        "plans_h": "Тарифы и оплата",
        "trial_h": "Не готов платить?",
        "trial_sub": "Бесплатно и без карты. Когда закончится, просто остановится: ничего не спишется.",
        "trial_items": lambda v: ["Сделки в личку", "VIP-канал", f"{v} {ru_plural(v, 'проверка', 'проверки', 'проверок')} VIN на весь срок"],
        "trial_go": "Начать бесплатно",
        "plans_note": lambda w, m1, m2: f"Платные тарифы действуют, пока не отменишь. Проверки VIN обновляются каждый период: {w} в неделю на Fast, {m1} или {m2} в месяц на VIP и PRO.",
        "period": {"week": "/ 7 дней", "month": "/ мес"},
        "feat": {
            "fast": lambda n, f, g: ["Сделки в личку", "VIP-канал", f"{n} проверок VIN", f"{f} фильтров, {g} машин в гараже"],
            "vip": lambda n, f, g: ["Всё из Fast", f"{n} проверок VIN", f"{f} фильтров, {g} машин в гараже", "Приоритетные алерты"],
            "pro": lambda n, f, g: ["Всё из VIP", f"{n} проверок VIN", "Безлимит фильтров и гаража", "Алерты первым"],
        },
        "get": lambda p: f"Оформить {p}",
        "recommended": "Рекомендуем",
        "per_month": lambda m: f"≈ €{m} / мес*",
        "promo": lambda p: f"Акция до 31 декабря. Цена €{p} остаётся, пока подписка активна.",
        "footnote": lambda m: f"* Fast продлевается каждую неделю: €6 × 4,3 недели ≈ €{m} в месяц.",
        "tag": {"fast": ("Срочно нужна машина", "Неделя полного доступа, пока ищешь прямо сейчас."),
                "vip": ("Без спешки и без переплаты", "Ищешь спокойно, сделки сами приходят каждый день."),
                "pro": ("Для перекупов и дилеров", "Покупаешь на перепродажу: больше всего проверок, алерты раньше всех.")},
        "guide_h": "Как оплатить и начать",
        "guide": ["Нажми на тариф и оплати в Tribute.",
                  "После оплаты Tribute даст доступ в VIP-канал.",
                  "Открой бота, нажми START и поставь фильтр. Тогда личные сделки пойдут в личку."],
        "guide_go": "Открыть бота",
        "fee": "Цены без сервисного сбора Tribute. Tribute добавляет его при оплате, и ты видишь его до подтверждения.",
        "pay_h": "Как устроена оплата",
        "pay": [
            ("Бот не видит твою карту.", "Кнопка оплаты открывает страницу Tribute. Карту вводишь там, к нам она не попадает."),
            ("Мы не храним ничего об оплате.", "У нас только твой Telegram id, тариф, его срок и фильтры. Номера карты, который мог бы утечь, нет."),
            ("Кто получает деньги.", "TRBT Limited (Кипр, HE 443898), компания, которая стоит за Tribute. Это имя будет в выписке банка."),
            ("Нет карты? Не страшно.", "Кроме карты, у Tribute есть другие способы оплаты. Набор зависит от устройства и страны, полный список видно перед оплатой."),
            ("Есть сервисный сбор.", "Tribute добавляет свой сбор поверх цены тарифа. Полную сумму ты видишь при оплате, до подтверждения."),
            ("Отмена в одном месте.", "Тариф управляется и отменяется внутри Tribute."),
        ],
        "contacts_h": "Контакты и соцсети", "questions": "Вопросы? Пиши на",
        "tg_channel": "Telegram-канал",
        "legal": ["Политика конфиденциальности", "Условия использования", "Удаление данных"],
        "legal_suffix": " (EN)",
    },
    "ka": {
        "title": "CarHunter World: მანქანები ბაზარზე იაფად",
        "desc": "Telegram-ბოტი, რომელიც ყოველდღე პოულობს ბაზარზე იაფ მანქანებს. დააყენე ფილტრი და მიიღე საუკეთესო შეთავაზებები ჩატში.",
        "h1": "მანქანები ბაზარზე იაფად.", "h1_accent": "ყოველდღე.",
        "lead": "CarHunter მთელი დღე ამოწმებს განცხადებებს. როცა მანქანა მსგავსებზე ბევრად იაფია, "
                "Telegram-ში შეტყობინებას პირველი მიიღებ.",
        "sticker_days": lambda d: f"{d} დღე", "sticker_free": "უფასოდ",
        "sticker_note": lambda v: f"ბარათის გარეშე. შეთავაზებები, VIP\u2011არხი, {v} VIN\u2011შემოწმება.",
        "cta": "გახსენი ბოტი Telegram-ში",
        "nav_label": "ამ გვერდზე", "lang_label": "ენა",
        "nav": ["როგორ მუშაობს", "ტარიფები და გადახდა", "კონტაქტები და ქსელები"],
        "top_h": "კვირის ტოპ-3 შეთავაზება",
        "top_sub": lambda r: f"ყველაზე დიდი ფასდაკლებები რეალურ შეთავაზებებს შორის, რომლებიც ბოტმა გამოგზავნა, {r}. დააჭირე მანქანას, რომ დიდად ნახო.",
        "under": "ბაზარზე იაფი", "market": "ბაზარი", "km": "კმ",
        "strip_l": "მიიღე ასეთი შეთავაზებები პირველმა", "strip_r": "გახსენი ბოტი",
        "lot_aria": lambda c: f"{c}: მიიღე ასეთი შეთავაზებები პირველმა Telegram-ში",
        "thumb_aria": lambda c: f"აჩვენე {c} დიდად", "photo_alt": lambda c: f"{c}, ფოტო განცხადებიდან",
        "how_h": "როგორ მუშაობს",
        "steps": [
            ("დააყენე ფილტრი", "ორი კითხვა: რამდენით იაფი უნდა იყოს ბაზარზე და რა ბიუჯეტი გაქვს. მარკა, ასაკი და გარბენი სურვილისამებრ."),
            ("მიიღე შეთავაზებები პირველმა", "იაფი მანქანები Telegram-ში მოგდის. თითოეულთან ჩანს ბაზრის ფასი, ასე რომ, მარტივად შეამოწმებ."),
            ("შეამოწმე VIN", "გამოგზავნე VIN ან VIN-ფირფიტის ფოტო. ნახავ აშშ-ის აუქციონების ისტორიას: salvage სტატუსს და ავარიებს."),
        ],
        "plans_h": "ტარიფები და გადახდა",
        "trial_h": "ჯერ არ ხარ მზად გადასახდელად?",
        "trial_sub": "უფასოდ და ბარათის გარეშე. როცა დასრულდება, უბრალოდ გაჩერდება: არაფერი ჩამოგეჭრება.",
        "trial_items": lambda v: ["შეთავაზებები პირად შეტყობინებებში", "VIP-არხი", f"სულ {v} VIN-შემოწმება"],
        "trial_go": "დაიწყე უფასოდ",
        "plans_note": lambda w, m1, m2: f"ფასიანი ტარიფები მოქმედებს, სანამ არ გააუქმებ. VIN-შემოწმებები ყოველ პერიოდში ახლდება: Fast-ზე კვირაში {w}, VIP-სა და PRO-ზე თვეში {m1} ან {m2}.",
        "period": {"week": "/ 7 დღე", "month": "/ თვე"},
        "feat": {
            "fast": lambda n, f, g: ["შეთავაზებები პირად შეტყობინებებში", "VIP-არხი", f"{n} VIN-შემოწმება", f"{f} ფილტრი, {g} მანქანა გარაჟში"],
            "vip": lambda n, f, g: ["ყველაფერი Fast-დან", f"{n} VIN-შემოწმება", f"{f} ფილტრი, {g} მანქანა გარაჟში", "პრიორიტეტული შეტყობინებები"],
            "pro": lambda n, f, g: ["ყველაფერი VIP-დან", f"{n} VIN-შემოწმება", "ულიმიტო ფილტრი და გარაჟი", "შეტყობინებები პირველ რიგში"],
        },
        "get": lambda p: f"აირჩიე {p}",
        "recommended": "გირჩევთ",
        "per_month": lambda m: f"≈ €{m} / თვე*",
        "promo": lambda p: f"აქცია 31 დეკემბრამდე. ფასი €{p} შენარჩუნდება, სანამ გამოწერა აქტიურია.",
        "footnote": lambda m: f"* Fast ყოველ კვირას გრძელდება: €6 × 4,3 კვირა ≈ €{m} თვეში.",
        "tag": {"fast": ("მანქანა სასწრაფოდ გჭირდება", "სრული წვდომის კვირა, სანამ ახლავე ეძებ."),
                "vip": ("აჩქარებისა და ზედმეტი ხარჯის გარეშე", "მშვიდად ეძებ, შეთავაზებები ყოველდღე თავად მოდის."),
                "pro": ("გადამყიდველებისა და დილერებისთვის", "ყიდულობ გასაყიდად: ყველაზე მეტი შემოწმება, შეტყობინებები ყველაზე ადრე.")},
        "guide_h": "როგორ გადავიხადო და დავიწყო",
        "guide": ["დააჭირე ტარიფს და გადაიხადე Tribute-ში.",
                  "გადახდის შემდეგ Tribute VIP-არხზე წვდომას მოგცემს.",
                  "გახსენი ბოტი, დააჭირე START-ს და დააყენე ფილტრი. მაშინ პირადი შეთავაზებები პირად შეტყობინებებში მოვა."],
        "guide_go": "გახსენი ბოტი",
        "fee": "ფასები მოცემულია Tribute-ის მომსახურების საკომისიოს გარეშე. Tribute მას გადახდისას ამატებს და დადასტურებამდე დაინახავ.",
        "pay_h": "როგორ ხდება გადახდა",
        "pay": [
            ("ბოტი შენს ბარათს ვერ ხედავს.", "გადახდის ღილაკი Tribute-ის გვერდს ხსნის. ბარათს იქ შეიყვან და ჩვენამდე არ აღწევს."),
            ("გადახდაზე არაფერს ვინახავთ.", "ვინახავთ შენს Telegram id-ს, ტარიფს, მის ვადას და ფილტრებს. ბარათის ნომერი ჩვენთან არ არის."),
            ("ვინ იღებს ფულს.", "TRBT Limited (კვიპროსი, HE 443898), კომპანია, რომელიც Tribute-ს უდგას უკან. ეს სახელი ჩანს ბანკის ამონაწერში."),
            ("ბარათი არ გაქვს? არა უშავს.", "ბარათის გარდა, Tribute-ს სხვა გადახდის გზებიც აქვს. ნაკრები მოწყობილობასა და ქვეყანაზეა დამოკიდებული, სრულ სიას გადახდამდე ნახავ."),
            ("არის მომსახურების საკომისიო.", "Tribute ტარიფის ფასს თავის საკომისიოს ამატებს. სრულ თანხას გადახდისას, დადასტურებამდე ხედავ."),
            ("გაუქმება ერთ ადგილას.", "ტარიფს Tribute-ში მართავ და იქვე აუქმებ."),
        ],
        "contacts_h": "კონტაქტები და ქსელები", "questions": "კითხვები გაქვს? მოგვწერე:",
        "tg_channel": "Telegram-არხი",
        "legal": ["კონფიდენციალურობის პოლიტიკა", "გამოყენების პირობები", "მონაცემების წაშლა"],
        "legal_suffix": " (EN)",
    },
    "fa": {
        "title": "CarHunter World: خودرو زیر قیمت بازار",
        "desc": "ربات تلگرامی که هر روز خودروهای زیر قیمت بازار را پیدا می‌کند. فیلتر بگذار و بهترین پیشنهادها را در چت بگیر.",
        "h1": "خودرو زیر قیمت بازار.", "h1_accent": "هر روز.",
        "lead": "CarHunter تمام روز آگهی‌ها را بررسی می‌کند. وقتی خودرویی خیلی ارزان‌تر از خودروهای مشابه باشد، "
                "اول از همه در تلگرام به تو پیام می‌دهد.",
        "sticker_days": lambda d: f"{d} روز", "sticker_free": "رایگان",
        "sticker_note": lambda v: f"بدون کارت. پیشنهادها، کانال VIP، {v} بررسی VIN.",
        "cta": "باز کردن ربات در تلگرام",
        "nav_label": "در این صفحه", "lang_label": "زبان",
        "nav": ["چطور کار می‌کند", "پلن‌ها و پرداخت", "تماس و شبکه‌های اجتماعی"],
        "top_h": "۳ پیشنهاد برتر این هفته",
        "top_sub": lambda r: f"بزرگ‌ترین تخفیف‌ها میان پیشنهادهای واقعی که ربات فرستاده، {r}. روی یک خودرو بزن تا بزرگ ببینی.",
        "under": "زیر قیمت بازار", "market": "بازار", "km": "کیلومتر",
        "strip_l": "پیشنهادهایی مثل این را زودتر بگیر", "strip_r": "باز کردن ربات",
        "lot_aria": lambda c: f"{c}: پیشنهادهایی مثل این را زودتر در تلگرام بگیر",
        "thumb_aria": lambda c: f"نمایش بزرگ {c}", "photo_alt": lambda c: f"{c}، عکس از آگهی",
        "how_h": "چطور کار می‌کند",
        "steps": [
            ("فیلتر بگذار", "دو سؤال: چقدر زیر قیمت بازار، و بودجه‌ات. برند، سن و کارکرد اختیاری است."),
            ("پیشنهادها را زودتر بگیر", "خودروهای ارزان به پیام‌های تلگرامت می‌آیند. قیمت بازار کنار هر کدام هست، پس راحت بررسی می‌کنی."),
            ("VIN را بررسی کن", "VIN یا عکس پلاک VIN را بفرست. تاریخچهٔ حراجی‌های آمریکا را می‌بینی: وضعیت salvage و تصادف‌ها."),
        ],
        "plans_h": "پلن‌ها و پرداخت",
        "trial_h": "هنوز آمادهٔ پرداخت نیستی؟",
        "trial_sub": "رایگان و بدون کارت. وقتی تمام شود، فقط متوقف می‌شود: هیچ پولی کسر نمی‌شود.",
        "trial_items": lambda v: ["پیشنهادها در پیام‌هایت", "کانال VIP", f"در کل {v} بررسی VIN"],
        "trial_go": "شروع رایگان",
        "plans_note": lambda w, m1, m2: f"پلن‌های پولی تا وقتی لغوشان نکنی فعال می‌مانند. بررسی‌های VIN هر دوره تازه می‌شوند: در Fast هفته‌ای {w}، در VIP و PRO ماهی {m1} یا {m2}.",
        "period": {"week": "/ ۷ روز", "month": "/ ماه"},
        "feat": {
            "fast": lambda n, f, g: ["پیشنهادها در پیام‌هایت", "کانال VIP", f"{n} بررسی VIN", f"{f} فیلتر، {g} خودرو در گاراژ"],
            "vip": lambda n, f, g: ["همهٔ امکانات Fast", f"{n} بررسی VIN", f"{f} فیلتر، {g} خودرو در گاراژ", "هشدار با اولویت"],
            "pro": lambda n, f, g: ["همهٔ امکانات VIP", f"{n} بررسی VIN", "فیلتر و گاراژ نامحدود", "هشدار زودتر از همه"],
        },
        "get": lambda p: f"گرفتن {p}",
        "recommended": "پیشنهاد ما",
        "per_month": lambda m: f"≈ ⁦€{m}⁩ / ماه*",  # LRI/PDI: keep "€26" in LTR order
        "promo": lambda p: f"تخفیف تا ۳۱ دسامبر. قیمت ⁦€{p}⁩ تا وقتی اشتراکت فعال است ثابت می‌ماند.",
        "footnote": lambda m: f"* Fast هر هفته تمدید می‌شود: ⁦€6⁩ × ۴٫۳ هفته ≈ ⁦€{m}⁩ در ماه.",
        "tag": {"fast": ("فوری خودرو لازم داری", "یک هفته دسترسی کامل، وقتی همین حالا دنبال خرید هستی."),
                "vip": ("بدون عجله و بدون هزینهٔ اضافه", "با خیال راحت بگرد، پیشنهادها هر روز خودشان می‌رسند."),
                "pro": ("برای خرید و فروش حرفه‌ای", "برای فروش دوباره می‌خری: بیشترین بررسی‌ها، هشدار زودتر از همه.")},
        "guide_h": "چطور پرداخت کنم و شروع کنم",
        "guide": ["روی یک پلن بزن و در Tribute پرداخت کن.",
                  "بعد از پرداخت، Tribute به تو دسترسی کانال VIP را می‌دهد.",
                  "ربات را باز کن، START را بزن و یک فیلتر بگذار. آن‌وقت پیشنهادهای شخصی به پیام‌هایت می‌آید."],
        "guide_go": "باز کردن ربات",
        "fee": "قیمت‌ها بدون کارمزد خدمات Tribute است. Tribute آن را هنگام پرداخت اضافه می‌کند و قبل از تأیید آن را می‌بینی.",
        "pay_h": "پرداخت چطور انجام می‌شود",
        "pay": [
            ("ربات کارتت را نمی‌بیند.", "دکمهٔ پرداخت صفحهٔ پرداخت Tribute را باز می‌کند. کارت را آنجا وارد می‌کنی و به ما نمی‌رسد."),
            ("ما هیچ اطلاعات پرداختی نگه نمی‌داریم.", "فقط شناسهٔ تلگرام، پلن، تاریخ پایان آن و فیلترهایت را نگه می‌داریم. شماره کارتی نزد ما نیست که لو برود."),
            ("چه کسی پول را می‌گیرد.", "TRBT Limited (قبرس، HE 443898)، شرکتی که پشت Tribute است. همین نام در صورت‌حساب بانکی‌ات دیده می‌شود."),
            ("کارت نداری؟ اشکالی ندارد.", "به‌جز کارت، Tribute راه‌های دیگری هم برای پرداخت دارد. مجموعه به دستگاه و کشورت بستگی دارد و فهرست کامل را قبل از پرداخت می‌بینی."),
            ("کارمزد خدمات وجود دارد.", "Tribute کارمزد خودش را روی قیمت پلن اضافه می‌کند. مبلغ کامل را هنگام پرداخت، قبل از تأیید می‌بینی."),
            ("لغو در یک جا.", "پلن را داخل Tribute مدیریت و لغو می‌کنی."),
        ],
        "contacts_h": "تماس و شبکه‌های اجتماعی", "questions": "سؤالی داری؟ بنویس به",
        "tg_channel": "کانال تلگرام",
        "legal": ["سیاست حریم خصوصی", "شرایط استفاده", "حذف داده‌ها"],
        "legal_suffix": " (EN)",
    },
}

SOCIAL = [
    ("Instagram", "https://www.instagram.com/carhunterworld/",
     '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>'),
    ("Facebook", "https://www.facebook.com/carhunterworld",
     '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>'),
    ("TikTok", "https://www.tiktok.com/@carhunterworld",
     '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 3c.5 2.8 2.4 4.5 5 4.8"/>'),
    (None, "https://t.me/carhunterworld",
     '<path d="M21 3 10.5 13.5"/><path d="M21 3 14.5 21l-4-7.5L3 9.5 21 3Z"/>'),
]

ARROW = ('<svg aria-hidden="true" class="arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></svg>')
SCOPE = ('<svg aria-hidden="true" width="34" height="34" viewBox="0 0 28 28" fill="none" stroke="currentColor" '
         'stroke-width="1.8" stroke-linecap="round"><circle cx="14" cy="14" r="9"/><circle cx="14" cy="14" r="3.5"/>'
         '<path d="M14 1.5v6M14 20.5v6M1.5 14h6M20.5 14h6"/></svg>')
CHECK = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>')
GLASS_PATH = ("M96 34 C420 8 780 8 1104 34 Q1150 38 1158 80 L1194 568 Q1198 624 1144 628 C790 640 410 640 "
              "56 628 Q2 624 6 568 L42 80 Q50 38 96 34 Z")


# The heading says "this week" in every language, so an old deals.json would be a quiet lie.
MAX_DEALS_AGE_DAYS = 8


def deals(stale_ok: bool = False) -> dict:
    data = json.loads((Path(__file__).resolve().parent / "deals.json").read_text(encoding="utf-8"))
    age = (date.today() - date.fromisoformat(data["to"])).days
    if age > MAX_DEALS_AGE_DAYS and not stale_ok:
        raise SystemExit(f"deals.json is {age} days old: run python _src/pick_deals.py first "
                         "(or pass --stale-ok for a text-only fix)")
    return data


def lot(lang: str, i: int, d: dict) -> str:
    t, e = T[lang], escape
    car = d["car"]
    city = CITIES.get(d["city"], {}).get(lang, d["city"])
    where = f"{city}, {num(lang, d['km'])} {t['km']}" if d.get("km") else city
    day = short_date(lang, date.fromisoformat(d["day"]))
    off = f"−{d['off']}%"
    on = i == 0
    return f"""<div class="slide {'on' if on else 'off'}" data-slide>
<a class="lotlink" href="{bot_url(d['id'])}" data-k="lot" aria-label="{e(t['lot_aria'](car))}">
<article class="bigglass">
<svg aria-hidden="true" viewBox="0 0 1200 640" preserveAspectRatio="none" class="glass-svg">
<defs><linearGradient id="gl{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1B4C8A"/><stop offset="1" stop-color="#0A2352"/></linearGradient>
<linearGradient id="rf{i}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>
<path d="{GLASS_PATH}" fill="url(#gl{i})" stroke="#030C22" stroke-width="12"/>
<path d="M640 40 L800 40 L560 624 L400 624 Z" fill="url(#rf{i})"/>
<rect x="556" y="0" width="88" height="28" rx="9" fill="#030C22"/>
</svg>
<div class="big-ui">
<span class="badge"><bdi dir="ltr">{off}</bdi> <small>{e(t['under'])}</small></span>
<figure class="photo"><span class="tape" aria-hidden="true"></span>
<img src="{d['img']}" alt="{e(t['photo_alt'](car))}" width="720" height="540" loading="lazy">
<figcaption>{e(day)}</figcaption></figure>
<div class="mk scrawl">
<div class="oneline car" dir="ltr">{e(car)}</div>
<div class="oneline price" dir="ltr">{usd(d['price_usd'])}</div>
<div class="oneline was"><span>{e(t['market'])}</span> <bdi dir="ltr">~{usd(d['market_usd'])}</bdi></div>
</div>
<p class="mk oneline where">{e(where)}</p>
</div>
</article>
<span class="strip"><span class="oneline">{e(t['strip_l'])}</span><span class="strip-go">{e(t['strip_r'])}{ARROW}</span></span>
</a>
<button class="thumb" type="button" data-pick aria-label="{e(t['thumb_aria'](car))}">
<span class="mini">
<svg aria-hidden="true" viewBox="0 0 1200 640" preserveAspectRatio="none" class="glass-svg"><path d="{GLASS_PATH}" fill="#123A70" stroke="#030C22" stroke-width="22"/></svg>
<span class="mk mini-ui"><span class="oneline mini-price" dir="ltr">{usd(d['price_usd'])}</span><span class="oneline mini-was" dir="ltr">~{usd(d['market_usd'])}</span></span>
<span class="mini-badge" dir="ltr">{off}</span>
</span>
<span class="oneline mini-car" dir="ltr">{e(car)}</span>
<span class="mini-where">{e(where)}</span>
</button>
</div>"""


def plans(lang: str) -> str:
    t, e = T[lang], escape
    out = []
    for pid, name, eur, period, vin, filters, garage, old in PLANS:
        feats = "".join(f"<li>{e(x)}</li>" for x in t["feat"][pid](num(lang, vin), num(lang, filters),
                                                                    num(lang, garage)))
        cls = "plan plan-hi" if pid == "vip" else "plan"
        badge = f'<span class="plan-badge">{e(t["recommended"])}</span>' if pid == "vip" else ""
        alt = (t["per_month"](FAST_MONTH_EUR) if pid == "fast"
               else t["promo"](eur) if old else "")
        was = f'<s class="was">€{old}</s> ' if old else ""
        tag, line = t["tag"][pid]
        out.append(f"""<article class="{cls}">
{badge}<h3 class="cond">{name}</h3>
<p class="plan-tag">{e(tag)}</p>
<p class="plan-line">{e(line)}</p>
<p class="plan-price">{was}<span class="cond" dir="ltr">€{eur}</span> <span class="per">{e(t['period'][period])}</span></p>
<p class="plan-alt" dir="auto">{e(alt)}</p>
<ul>{feats}</ul>
<a class="go plan-go" href="{TRIBUTE[pid]}" data-k="plan" data-p="{pid}">{e(t['get'](name))}{ARROW}</a>
</article>""")
    return "".join(out)


def page(lang: str, data: dict) -> str:
    t, e = T[lang], escape
    path = dict((code, url) for code, _, url in LANGS)[lang]
    rtl = ' dir="rtl"' if lang == "fa" else ""
    auto = ' data-autolang="1"' if lang == "en" else ""
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{code}" href="{SITE}{url}">' for code, _, url in LANGS
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/">'
    langs = "".join(
        f'<a class="lang" href="{url}" data-lang="{code}" lang="{code}" title="{e(name)}"'
        + (' aria-current="page"' if code == lang else "")
        + f">{code.upper()}</a>"
        for code, name, url in LANGS
    )
    pills = "".join(f'<a class="pill" href="#{a}">{e(x)}</a>'
                    for a, x in zip(["how", "plans", "contacts"], t["nav"]))
    rng = date_range(lang, date.fromisoformat(data["from"]), date.fromisoformat(data["to"]))
    lots = "".join(lot(lang, i, d) for i, d in enumerate(data["deals"]))
    steps = "".join(f'<div class="lane-step{" r" if i % 2 else ""}"><h3 class="cond">{e(h)}</h3><p>{e(p)}</p></div>'
                    for i, (h, p) in enumerate(t["steps"]))
    items = t["trial_items"](num(lang, TRIAL_VIN))
    # The last item is the VIN pack, the one real limit of the trial, so it gets the gold.
    trial_items = "".join(f'<li class="{"trial-vin" if i == len(items) - 1 else ""}">{CHECK}{e(x)}</li>'
                          for i, x in enumerate(items))
    pay = "".join(f"<div><strong>{e(h)}</strong><p>{e(p)}</p></div>" for h, p in t["pay"])
    fee = t["fee"]
    guide = "".join(f"<li>{e(x)}</li>" for x in t["guide"])
    social = "".join(
        f'<a class="pill soc" href="{url}"><svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icon}</svg>'
        f'{e(label or t["tg_channel"])}</a>'
        for label, url, icon in SOCIAL
    )
    legal = "".join(
        f'<a href="/{href}">{e(name)}{e(t["legal_suffix"])}</a>'
        for href, name in zip(["privacy.html", "terms.html", "data-deletion.html"], t["legal"])
    )
    d, v = num(lang, TRIAL_DAYS), num(lang, TRIAL_VIN)
    return f"""<!doctype html>
<html lang="{lang}"{rtl}{auto}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t["title"])}</title>
<meta name="description" content="{e(t["desc"])}">
<meta name="theme-color" content="#061633">
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

<header class="top wrap">
<a class="brand" href="{path}">{SCOPE}<span class="cond">CarHunter World</span></a>
<nav class="langs" aria-label="{e(t['lang_label'])}">{langs}</nav>
</header>

<main>
<section class="hero wrap">
<div class="hero-top">
<div>
<h1 class="cond">{e(t["h1"])} <span>{e(t["h1_accent"])}</span></h1>
<p class="lead">{e(t["lead"])}</p>
</div>
</div>
<div class="hero-actions">
<a class="go go-big" href="{bot_url()}" data-k="cta">{e(t["cta"])}{ARROW}</a>
<nav class="pills" aria-label="{e(t['nav_label'])}">{pills}</nav>
</div>
</section>

<section class="wrap top3" aria-labelledby="lot-h">
<h2 id="lot-h" class="cond">{e(t["top_h"])}</h2>
<p class="sub">{e(t["top_sub"](rng))}</p>
<div class="lots">{lots}</div>
</section>

<section id="how" class="wrap how" aria-labelledby="how-h">
<h2 id="how-h" class="cond">{e(t["how_h"])}</h2>
<div class="lane"><div class="lane-line" aria-hidden="true"></div>{steps}</div>
</section>

<section id="plans" class="plans-band" aria-labelledby="plans-h">
<div class="wrap">
<h2 id="plans-h" class="cond">{e(t["plans_h"])}</h2>
<p class="plans-note">{e(t["plans_note"](*(num(lang, p[4]) for p in PLANS)))}</p>
<div class="plans">{plans(lang)}</div>
<p class="fee">{e(t["footnote"](FAST_MONTH_EUR))}<br>{e(fee)}</p>
<div class="guide">
<h3 class="cond">{e(t["guide_h"])}</h3>
<ol>{guide}</ol>
<a class="go guide-go" href="{bot_url()}" data-k="guide">{e(t["guide_go"])}{ARROW}</a>
</div>
<div class="trial">
<div class="trial-head">
<span class="trial-tag">{e(t["trial_h"])}</span>
<span class="cond trial-days">{e(t["sticker_days"](d))}</span>
<p>{e(t["trial_sub"])}</p>
</div>
<ul class="trial-list">{trial_items}</ul>
<a class="go trial-go" href="{bot_url()}" data-k="trial">{e(t["trial_go"])}{ARROW}</a>
</div>
<h3 class="cond pay-h">{e(t["pay_h"])}</h3>
<div class="pay">{pay}</div>
</div>
</section>

<section id="contacts" class="wrap contacts" aria-labelledby="contacts-h">
<h2 id="contacts-h" class="cond">{e(t["contacts_h"])}</h2>
<p class="ask">{e(t["questions"])} <a href="mailto:hello@carhunterworld.com">hello@carhunterworld.com</a></p>
<div class="social">{social}</div>
<footer>{legal}</footer>
</section>
</main>

<script>
// Expanding panels: a tap on a small windshield makes it the big one. Without JS the first
// deal stays big and the page still works.
document.querySelectorAll('[data-pick]').forEach(function (b) {{
  b.addEventListener('click', function () {{
    var slide = b.closest('[data-slide]');
    document.querySelectorAll('[data-slide]').forEach(function (s) {{
      s.classList.toggle('on', s === slide); s.classList.toggle('off', s !== slide);
    }});
    var link = slide.querySelector('.lotlink'); if (link) link.focus({{preventScroll: true}});
  }});
}});
// Source tag: an ad links here as ?src=gads, and every bot link then carries src_gads instead
// of src_site (kept for the visit, so a language switch keeps it). The bot reads at most 64
// characters of a start payload: a deal tail that would not fit is dropped, the tag is not.
// Then every button beacons its click, plan buttons too: they leave for Tribute, which knows
// no source. sendBeacon outlives the page; nothing waits for it.
(function () {{
  var q = new URLSearchParams(location.search);
  var s = (q.get('src') || '').toLowerCase();
  if (!/^[a-z0-9_]{{1,24}}$/.test(s)) s = '';
  try {{ if (s) sessionStorage.setItem('chsrc', s); else s = sessionStorage.getItem('chsrc') || ''; }} catch (e) {{}}
  if (s) document.querySelectorAll('a[href*="?start=src_{SRC}"]').forEach(function (a) {{
    var h = a.href.replace('?start=src_{SRC}', '?start=src_' + s);
    if (h.split('?start=')[1].length > 64) h = h.split('__deal_')[0];
    a.href = h;
  }});
  var api = q.get('e') === 'dev' ? '{CLICK_API["dev"]}' : '{CLICK_API["prod"]}';
  document.querySelectorAll('[data-k]').forEach(function (a) {{
    a.addEventListener('click', function () {{
      var b = new URLSearchParams({{k: a.dataset.k, s: s || '{SRC}', l: document.documentElement.lang}});
      if (a.dataset.p) b.set('p', a.dataset.p);
      var sent = false;
      try {{ sent = navigator.sendBeacon(api, b); }} catch (e) {{}}
      if (!sent) try {{ fetch(api, {{method: 'POST', body: b, mode: 'no-cors', keepalive: true}}); }} catch (e) {{}}
    }});
  }});
}})();
</script>
</body>
</html>
"""


def main() -> None:
    data = deals(stale_ok="--stale-ok" in sys.argv)
    for code, _, url in LANGS:
        out = ROOT / url.strip("/") / "index.html" if url != "/" else ROOT / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(code, data), encoding="utf-8", newline="\n")
        print("wrote", out.relative_to(ROOT))
    # The bot reads this to show the lot a visitor tapped (site_funnel.find_deal): the same
    # numbers the page shows. Public anyway, they are on the page.
    (ROOT / "deals.json").write_text(json.dumps({"from": data["from"], "to": data["to"],
                                                 "deals": data["deals"]}, ensure_ascii=False,
                                                indent=1) + "\n", encoding="utf-8", newline="\n")
    print("wrote deals.json")


if __name__ == "__main__":
    main()
