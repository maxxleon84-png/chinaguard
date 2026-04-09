import asyncio
import logging
import sys

from config import MONITOR_BOT_TOKEN, CHECK_INTERVAL, TELEGRAM_API_ID
from db import init_db, post_exists, save_post
from ai import generate_draft
from bot import bot, dp, send_notification, is_paused
from parsers import ALL_PARSERS, setup_telegram_listener

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


async def check_platforms():
    if is_paused():
        return

    for parser_fn in ALL_PARSERS:
        try:
            posts = await parser_fn()
            log.info(f"{parser_fn.__name__}: found {len(posts)} matches")

            for post in posts:
                if await post_exists(post.url):
                    continue

                draft = await generate_draft(post.text)

                from keywords import match_keywords
                keyword = match_keywords(post.text) or "—"

                post_id = await save_post(
                    platform=post.platform,
                    post_url=post.url,
                    title=post.title,
                    matched_keyword=keyword,
                    draft_response=draft,
                )

                await send_notification(
                    post_id=post_id,
                    platform=post.platform,
                    url=post.url,
                    title=post.title,
                    draft=draft,
                )

                await asyncio.sleep(1)

        except Exception as e:
            log.error(f"Error in {parser_fn.__name__}: {e}")


async def scheduler():
    while True:
        log.info("Running platform check...")
        await check_platforms()
        log.info(f"Next check in {CHECK_INTERVAL // 60} min")
        await asyncio.sleep(CHECK_INTERVAL)


async def on_telegram_match(platform: str, url: str, title: str,
                            text: str, keyword: str):
    if is_paused():
        return
    if await post_exists(url):
        return

    draft = await generate_draft(text)
    post_id = await save_post(
        platform=platform,
        post_url=url,
        title=title,
        matched_keyword=keyword,
        draft_response=draft,
    )
    await send_notification(
        post_id=post_id,
        platform=platform,
        url=url,
        title=title,
        draft=draft,
    )


async def main():
    if not MONITOR_BOT_TOKEN:
        print("ERROR: Set MONITOR_BOT_TOKEN environment variable")
        sys.exit(1)

    await init_db()
    log.info("ChinaGuard Monitor started")

    telethon_client = setup_telegram_listener(on_telegram_match)
    if telethon_client:
        try:
            await telethon_client.start()
            log.info("Telethon: connected to Telegram chats")
        except Exception as e:
            log.warning(f"Telethon: failed to start ({e}), running without Telegram monitoring")
            telethon_client = None

    await asyncio.gather(
        scheduler(),
        dp.start_polling(bot),
    )


if __name__ == "__main__":
    asyncio.run(main())
