from telethon import TelegramClient, events
from keywords import match_keywords
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

MONITORED_CHATS = []

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
