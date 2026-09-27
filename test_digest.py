from datetime import datetime, timedelta
from models import Event
from digest import deduplicate, format_digest, select_events
from utils import MOSCOW_TZ

now = datetime.now(MOSCOW_TZ)
events = [
    Event("Фестиваль в парке", now + timedelta(hours=5), None, "ВДНХ", "https://example.com/1", "Test", "Большой бесплатный фестиваль", distance_km=8),
    Event("Фестиваль в парке", now + timedelta(hours=5), None, "ВДНХ", "https://example.com/2", "Test2", "Дубль", distance_km=8),
    Event("Бесплатная выставка", now + timedelta(days=2), None, "Москва", "https://example.com/3", "Test", "Выставка", registration_required=True),
]
selected = select_events(events)
assert len(selected) == 2, selected
text = format_digest(selected)
assert "Фестиваль" in text and "выставка" in text
print("OK")
