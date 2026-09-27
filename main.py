import sys

from config import SEARCH_DAYS
from digest import format_digest, select_events, split_telegram_html
from sources.kudago import fetch_kudago
from sources.timepad import fetch_timepad
from telegram_api import send_message


def collect_events():
    events = []
    errors = []
    for name, fn in (("KudaGo", fetch_kudago), ("Timepad", fetch_timepad)):
        try:
            events.extend(fn(SEARCH_DAYS))
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    if not events and errors:
        raise RuntimeError("; ".join(errors))
    return events, errors


def run(send=True):
    events, errors = collect_events()
    selected = select_events(events)
    message = format_digest(selected)
    if errors:
        message += "\n\n<i>⚠️ Один из источников временно не ответил; дайджест собран по остальным.</i>"
    if send:
        for chunk in split_telegram_html(message):
            send_message(chunk)
    else:
        print(message)


if __name__ == "__main__":
    run(send="--preview" not in sys.argv)
