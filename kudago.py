from datetime import datetime, timedelta
import requests

from config import MOSCOW_CENTER_LAT, MOSCOW_CENTER_LON, SEARCH_RADIUS_KM, TIMEOUT, USER_AGENT
from models import Event
from utils import clean_text, haversine_km, to_moscow_dt, MOSCOW_TZ

API = "https://kudago.com/public-api/v1.4/events/"


def fetch_kudago(days=7, limit_pages=4):
    now = datetime.now(MOSCOW_TZ)
    until = now + timedelta(days=days)
    params = {
        "lang": "ru",
        "fields": "id,title,description,dates,place,categories,age_restriction,is_free,price,site_url",
        "expand": "place",
        "actual_since": int(now.timestamp()),
        "actual_until": int(until.timestamp()),
        "is_free": 1,
        "lat": MOSCOW_CENTER_LAT,
        "lon": MOSCOW_CENTER_LON,
        "radius": int(SEARCH_RADIUS_KM * 1000),
        "page_size": 100,
        "order_by": "-publication_date",
    }
    headers = {"User-Agent": USER_AGENT}
    events = []
    url = API

    for _ in range(limit_pages):
        response = requests.get(url, params=params if url == API else None, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        for item in data.get("results", []):
            if not item.get("is_free"):
                continue
            place = item.get("place") or {}
            coords = place.get("coords") or {}
            lat, lon = coords.get("lat"), coords.get("lon")
            distance = None
            if lat is not None and lon is not None:
                distance = haversine_km(MOSCOW_CENTER_LAT, MOSCOW_CENTER_LON, float(lat), float(lon))
                if distance > SEARCH_RADIUS_KM:
                    continue

            address = place.get("address") or place.get("title") or "Москва / Московская область"
            dates = item.get("dates") or []
            for d in dates[:10]:
                start_raw = d.get("start")
                if not start_raw:
                    continue
                start = to_moscow_dt(start_raw)
                end = to_moscow_dt(d["end"]) if d.get("end") else None
                if start > until or (end and end < now):
                    continue
                events.append(Event(
                    title=clean_text(item.get("title"), 160),
                    start=start,
                    end=end,
                    address=clean_text(address, 180),
                    url=item.get("site_url") or "https://kudago.com/msk/",
                    source="KudaGo",
                    description=clean_text(item.get("description"), 260),
                    category=", ".join(item.get("categories") or []),
                    age=clean_text(item.get("age_restriction"), 20),
                    registration_required=None,
                    lat=float(lat) if lat is not None else None,
                    lon=float(lon) if lon is not None else None,
                    distance_km=distance,
                ))

        url = data.get("next")
        params = None
        if not url:
            break
    return events
