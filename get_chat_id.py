from telegram_api import get_updates


def main():
    data = get_updates()
    chats = {}
    for upd in data.get("result", []):
        msg = upd.get("message") or upd.get("channel_post") or {}
        chat = msg.get("chat") or {}
        if chat.get("id") is not None:
            chats[chat["id"]] = chat.get("title") or chat.get("username") or chat.get("first_name") or "chat"
    if not chats:
        print("Чаты не найдены. Напишите боту /start, затем запустите этот файл ещё раз.")
        return
    print("Найденные chat_id:")
    for chat_id, name in chats.items():
        print(f"{chat_id}  {name}")


if __name__ == "__main__":
    main()
