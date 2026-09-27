from datetime import datetime, timedelta
import requests

from config import MOSCOW_CENTER_LAT, MOSCOW_CENTER_LON, SEARCH_RADIUS_KM, TIMEOUT, USER_AGENT
from models import Event
from utils import clean_text, haversine_km, to_moscow_dt, MOSCOW_TZ

API = "https://api.timepad.ru/v1/events.json"
CITIES = [
    "Москва", "Химки", "Красногорск", "Одинцово", "Реутов", "Мытищи",
    "Люберцы", "Балашиха", "Долгопрудный", "Подольск", "Видное",
    "Королёв", "Королев", "Щёлково", "Щелково", "Лобня", "Котельники",
    "Дзержинский", "Домодедово", "Истра", "Нахабино", "Московский"
]


def fetch_timepad(days=7, limit_pages=4):
    now = datetime.now(MOSCOW_TZ)
    until = now + timedelta(days=days)
    headers = {"User-Agent": USER_AGENT}
    events = []

    # Timepad supports comma-separated cities. price_max=0 keeps events with a free ticket.
    for page in range(limit_pages):
        params = {
            "limit": 100,
            "skip": page * 100,
            "cities": ",".join(CITIES),
            "fields": "location,registration_data,description_short,organization",
            "sort": "+starts_at",
            "starts_at_min": now.isoformat(),
            "starts_at_max": until.isoformat(),
            "price_max": 0,
        }
        response = requests.get(API, params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        values = data.get("values") or data.get("results") or []
        if not values:
            break

        for item in values:
            reg = item.get("registration_data") or {}
            pmin = reg.get("price_min")
            # Be conservative: include only explicit zero/free results.
            if pmin not in (0, 0.0, None):
                continue

            loc = item.get("location") or {}
            coords = loc.get("coordinates") or []
            lat = lon = distance = None
            if len(coords) >= 2:
                # Timepad docs define coordinates as latitude, longitude.
                lat, lon = float(coords[0]), float(coords[1])
                distance = haversine_km(MOSCOW_CENTER_LAT, MOSCOW_CENTER_LON, lat, lon)
                if distance > SEARCH_RADIUS_KM:
                    continue

            address = ", ".join(x for x in [loc.get("city"), loc.get("address")] if x) or "Москва / Московская область"
            start_raw = item.get("starts_at")
            if not start_raw:
                continue
            start = to_moscow_dt(start_raw)
            end = to_moscow_dt(item["ends_at"]) if item.get("ends_at") else None

            events.append(Event(
                title=clean_text(item.get("name"), 160),
                start=start,
                end=end,
                address=clean_text(address, 180),
                url=item.get("url") or "https://timepad.ru/",
                source="Timepad",
                description=clean_text(item.get("description_short"), 260),
                category="",
                age=clean_text(item.get("age_limit"), 20),
                registration_required=True if reg else None,
                lat=lat,
                lon=lon,
                distance_km=distance,
            ))
        if len(values) < 100:
            break
    return events
