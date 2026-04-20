"""Одноразовый скрипт для перелогина в Telegram.

Запускать вручную, когда сессия протухла:
    python relogin.py

Спросит телефон, код из СМС и пароль 2FA (если есть).
После успеха создастся свежий monitor_session.session, и main.py заработает.
"""
import asyncio
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH


async def main():
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("ERROR: TELEGRAM_API_ID/TELEGRAM_API_HASH не заданы в .env")
        return

    client = TelegramClient("monitor_session", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    print("Запускаю авторизацию...")
    await client.start()
    me = await client.get_me()
    print(f"\nГотово! Залогинен как: {me.first_name} (@{me.username}, id={me.id})")
    print("Сессия сохранена в monitor_session.session — теперь запусти main.py")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
