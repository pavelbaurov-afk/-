import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
MAX_EVENTS = int(os.getenv("MAX_EVENTS", "18"))
SEARCH_DAYS = int(os.getenv("SEARCH_DAYS", "7"))
MOSCOW_CENTER_LAT = float(os.getenv("MOSCOW_CENTER_LAT", "55.7558"))
MOSCOW_CENTER_LON = float(os.getenv("MOSCOW_CENTER_LON", "37.6173"))
# ~55 km from central Moscow is a practical approximation of Moscow + ~30 km beyond MKAD.
SEARCH_RADIUS_KM = float(os.getenv("SEARCH_RADIUS_KM", "55"))
TIMEOUT = 25
USER_AGENT = "MoscowFreeEventsBot/1.0 (+Telegram digest)"
