import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import Command

from config import MONITOR_BOT_TOKEN, ADMIN_ID
from db import update_post_status, get_stats

router = Router()
bot = Bot(token=MONITOR_BOT_TOKEN) if MONITOR_BOT_TOKEN else None
dp = Dispatcher()
dp.include_router(router)

_paused = False


async def send_notification(post_id: int, platform: str, url: str,
                            title: str, draft: str):
    if not bot or _paused:
        return

    text = (
        f"📌 {platform} — новый пост\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"{title[:300]}\n\n"
        f"🔗 {url}\n\n"
        f"💬 Черновик ответа:\n"
        f"{draft[:800]}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 Скопировать ответ",
                callback_data=f"copy:{post_id}",
            ),
            InlineKeyboardButton(
                text="⏭ Пропустить",
                callback_data=f"skip:{post_id}",
            ),
        ]
    ])

    await bot.send_message(ADMIN_ID, text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("copy:"))
async def on_copy(callback: CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    msg_text = callback.message.text or ""
    draft_start = msg_text.find("💬 Черновик ответа:\n")
    if draft_start != -1:
        draft = msg_text[draft_start + len("💬 Черновик ответа:\n"):]
        await callback.message.answer(f"```\n{draft}\n```", parse_mode="Markdown")
    await update_post_status(post_id, "copied")
    await callback.answer("Черновик отправлен для копирования")


@router.callback_query(F.data.startswith("skip:"))
async def on_skip(callback: CallbackQuery):
    post_id = int(callback.data.split(":")[1])
    await update_post_status(post_id, "skipped")
    await callback.answer("Пропущено")
    await callback.message.edit_reply_markup(reply_markup=None)


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    stats = await get_stats()
    await message.answer(
        f"📊 Статистика мониторинга\n\n"
        f"Сегодня: {stats['today']}\n"
        f"За неделю: {stats['week']}\n"
        f"За месяц: {stats['month']}\n"
        f"Всего: {stats['total']}"
    )


@router.message(Command("pause"))
async def cmd_pause(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    global _paused
    _paused = True
    await message.answer("⏸ Мониторинг приостановлен. /resume для продолжения.")


@router.message(Command("resume"))
async def cmd_resume(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    global _paused
    _paused = False
    await message.answer("▶️ Мониторинг возобновлён.")


@router.message(Command("keywords"))
async def cmd_keywords(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    from keywords import KEYWORDS_EXACT, KEYWORDS_BROAD, BROAD_PLATFORMS

    await message.answer(
        f"🎯 Точные триггеры ({len(KEYWORDS_EXACT)}) — все площадки:"
    )
    for i in range(0, len(KEYWORDS_EXACT), 15):
        chunk = KEYWORDS_EXACT[i:i+15]
        await message.answer("\n".join(f"• {kw}" for kw in chunk))

    await message.answer(
        f"🔍 Широкие триггеры ({len(KEYWORDS_BROAD)}) — только {', '.join(sorted(BROAD_PLATFORMS))}:"
    )
    for i in range(0, len(KEYWORDS_BROAD), 15):
        chunk = KEYWORDS_BROAD[i:i+15]
        await message.answer("\n".join(f"• {kw}" for kw in chunk))


def is_paused() -> bool:
    return _paused
