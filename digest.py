from collections import defaultdict
from datetime import datetime, timedelta
from html import escape

from config import MAX_EVENTS, MOSCOW_CENTER_LAT, MOSCOW_CENTER_LON
from models import Event
from utils import normalize_title, MOSCOW_TZ

INTEREST_WORDS = {
    "фестиваль": 4, "концерт": 3, "выстав": 2, "экскурс": 3,
    "ярмарк": 2, "лекц": 1, "спектак": 2, "дет": 2,
    "парк": 1, "мастер-класс": 1, "кинопоказ": 2, "музей": 2,
}


def deduplicate(events):
    seen = {}
    for ev in sorted(events, key=lambda x: x.start):
        key = (normalize_title(ev.title), ev.start.date())
        old = seen.get(key)
        if not old:
            seen[key] = ev
            continue
        # Prefer an entry with coordinates/address; otherwise keep the earliest one.
        old_quality = bool(old.lat) + bool(old.address) + (old.source == "KudaGo")
        new_quality = bool(ev.lat) + bool(ev.address) + (ev.source == "KudaGo")
        if new_quality > old_quality:
            seen[key] = ev
    return list(seen.values())


def score_events(events):
    now = datetime.now(MOSCOW_TZ)
    for ev in events:
        s = 0.0
        text = f"{ev.title} {ev.description} {ev.category}".lower()
        for word, weight in INTEREST_WORDS.items():
            if word in text:
                s += weight
        hours = max(0.0, (ev.start - now).total_seconds() / 3600)
        if hours <= 36:
            s += 4
        elif hours <= 72:
            s += 2
        if ev.distance_km is not None:
            s += max(0, 2.5 - ev.distance_km / 25)
        if ev.description:
            s += 0.5
        ev.score = s
    return events


def select_events(events, max_events=MAX_EVENTS):
    events = deduplicate(events)
    score_events(events)
    events.sort(key=lambda e: (-e.score, e.start, e.title.lower()))
    return events[:max_events]


def _date_label(dt):
    weekdays = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    return f"{dt:%d.%m} ({weekdays[dt.weekday()]}) {dt:%H:%M}"


def format_digest(events):
    now = datetime.now(MOSCOW_TZ)
    if not events:
        return (
            "<b>🎟 Бесплатно в Москве и рядом</b>\n\n"
            "На ближайшие дни подходящих событий из подключённых источников не найдено. "
            "Следующая проверка — завтра."
        )

    blocks = [
        f"<b>🎟 Куда сходить бесплатно</b>\n"
        f"Москва + ближайшее Подмосковье · {now:%d.%m.%Y}\n"
        f"Нашёл: <b>{len(events)}</b> вариантов\n"
    ]
    for i, ev in enumerate(events, 1):
        reg = " · нужна регистрация" if ev.registration_required else ""
        dist = f" · ~{ev.distance_km:.0f} км от центра" if ev.distance_km is not None else ""
        age = f" · {escape(ev.age)}" if ev.age else ""
        desc = f"\n{escape(ev.description)}" if ev.description else ""
        blocks.append(
            f"\n<b>{i}. {escape(ev.title)}</b>\n"
            f"📅 {_date_label(ev.start)}{age}\n"
            f"📍 {escape(ev.address)}{dist}\n"
            f"💰 Бесплатно{reg}{desc}\n"
            f"🔗 <a href=\"{escape(ev.url, quote=True)}\">Источник: {escape(ev.source)}</a>"
        )
    blocks.append("\n\n<i>Перед поездкой проверьте условия и регистрацию по ссылке: организаторы иногда меняют расписание.</i>")
    return "".join(blocks)


def split_telegram_html(text, limit=3900):
    if len(text) <= limit:
        return [text]
    chunks, current = [], ""
    for block in text.split("\n\n"):
        candidate = (current + "\n\n" + block).strip() if current else block
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = block
    if current:
        chunks.append(current)
    return chunks
