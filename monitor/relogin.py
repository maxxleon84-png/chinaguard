"""Одноразовый скрипт для перелогина в Telegram.

Запускать вручную, когда сессия протухла:
    python -u relogin.py

Спросит телефон, код из СМС и пароль 2FA (если есть).
После успеха создастся свежий monitor_session.session, и main.py заработает.
"""
import asyncio
import logging
import sys

from telethon import TelegramClient
from telethon.network import ConnectionTcpObfuscated
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)


def ask_phone():
    sys.stdout.write("\n>>> Телефон (с +, например +79991234567): ")
    sys.stdout.flush()
    return input()


def ask_code():
    sys.stdout.write("\n>>> Код из СМС / приложения Telegram: ")
    sys.stdout.flush()
    return input()


def ask_password():
    sys.stdout.write("\n>>> Пароль 2FA (Enter если не включён): ")
    sys.stdout.flush()
    return input()


async def main():
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("ERROR: TELEGRAM_API_ID/TELEGRAM_API_HASH не заданы в .env")
        return

    print("Запускаю авторизацию...", flush=True)
    client = TelegramClient(
        "monitor_session",
        TELEGRAM_API_ID,
        TELEGRAM_API_HASH,
        connection=ConnectionTcpObfuscated,
    )

    await client.start(
        phone=ask_phone,
        code_callback=ask_code,
        password=ask_password,
    )

    me = await client.get_me()
    print(
        f"\n✅ Готово! Залогинен как: {me.first_name} "
        f"(@{me.username}, id={me.id})",
        flush=True,
    )
    print("Сессия сохранена в monitor_session.session — теперь запусти main.py", flush=True)
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
