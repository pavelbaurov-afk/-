import requests

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TIMEOUT


def _require_token():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")


def send_message(text, chat_id=None):
    _require_token()
    target = str(chat_id or TELEGRAM_CHAT_ID).strip()
    if not target:
        raise RuntimeError("TELEGRAM_CHAT_ID is not set")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": target,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data


def get_updates():
    _require_token()
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    r = requests.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()
