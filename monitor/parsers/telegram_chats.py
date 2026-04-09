from telethon import TelegramClient, events
from keywords import match_keywords
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

MONITORED_CHATS = [
    # Чаты (обсуждения — основной источник лидов)
    "cargovik",               # Карго доставка из Китая (1.2K)
    "optlist_chat",           # База поставщиков ОптЛист (36K)
    "asiaimportgroup_community",  # Community Asia Import Group (900)
    "ved_logistika_perevozki_import",  # ВЭД, Логистика, Брокеры, Импорт, Таможня (2.3K)
    # Каналы (мониторим посты и комментарии)
    "proimport",              # Импорт в Россию (54K)
    "asiaresource",           # Оплата в Китай / Доставка из Китая (4K)
    "openchina",              # Open China — импорт, ВЭД (7.5K)
    "zaorro_sp",              # База поставщиков из Китая (4.9K)
    "postavki_china",         # Поставщик из Китая оптом (4.8K)
    "daoimportera",           # Дао Импортёра (5.8K)
]

client = TelegramClient(
    "monitor_session",
    TELEGRAM_API_ID,
    TELEGRAM_API_HASH,
)


def setup_telegram_listener(on_match_callback):
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("Telethon: API_ID/API_HASH not set, Telegram monitoring disabled")
        return None

    if not MONITORED_CHATS:
        print("Telethon: no chats to monitor, skipping")
        return None

    @client.on(events.NewMessage(chats=MONITORED_CHATS))
    async def handler(event):
        text = event.message.text or ""
        if not text or len(text) < 20:
            return

        keyword = match_keywords(text)
        if keyword:
            chat = await event.get_chat()
            chat_name = getattr(chat, "title", "Telegram")
            msg_link = f"https://t.me/c/{chat.id}/{event.message.id}"

            await on_match_callback(
                platform=f"telegram:{chat_name}",
                url=msg_link,
                title=text[:100],
                text=text[:1000],
                keyword=keyword,
            )

    return client
