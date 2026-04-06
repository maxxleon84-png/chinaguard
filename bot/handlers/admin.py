from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from bot.config import ADMIN_ID
from bot.db import get_active_orders, get_order, update_status

router = Router(name="admin")


def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


@router.message(Command("orders"), F.from_user.id == ADMIN_ID)
async def cmd_orders(message: Message) -> None:
    orders = await get_active_orders()
    if not orders:
        await message.answer("Нет активных заявок.")
        return

    lines: list[str] = ["📋 Активные заявки:\n"]
    for o in orders:
        desc = (o.get("description") or o.get("file_name") or "—")[:50]
        lines.append(
            f"#{o['id']} | @{o.get('username', 'N/A')} | {o['status']} | {desc}"
        )
    await message.answer("\n".join(lines))


@router.message(Command("status"), F.from_user.id == ADMIN_ID)
async def cmd_status(message: Message) -> None:
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Формат: /status <id> <accepted|in_progress|done>")
        return

    try:
        order_id = int(parts[1])
    except ValueError:
        await message.answer("ID заявки должен быть числом.")
        return

    new_status = parts[2].strip()
    ok = await update_status(order_id, new_status)
    if not ok:
        await message.answer(
            "Не удалось обновить статус. Проверьте ID и допустимые статусы: "
            "accepted, in_progress, done"
        )
        return

    await message.answer(f"Заявка #{order_id} → {new_status}")

    # Notify client when work starts
    if new_status == "in_progress":
        order = await get_order(order_id)
        if order:
            await message.bot.send_message(
                order["user_id"],
                f"Ваша заявка #{order_id} взята в работу. "
                "Специалист готовит отчёт.",
            )


@router.message(Command("send"), F.from_user.id == ADMIN_ID)
async def cmd_send(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Формат: /send <id> — ответьте на сообщение с PDF.")
        return

    try:
        order_id = int(parts[1])
    except ValueError:
        await message.answer("ID заявки должен быть числом.")
        return

    order = await get_order(order_id)
    if not order:
        await message.answer(f"Заявка #{order_id} не найдена.")
        return

    reply = message.reply_to_message
    if not reply or not reply.document:
        await message.answer(
            "Ответьте командой /send на сообщение с PDF-файлом."
        )
        return

    # Send PDF to client
    await message.bot.send_document(
        chat_id=order["user_id"],
        document=reply.document.file_id,
        caption=f"Отчёт по заявке #{order_id} готов. Спасибо за обращение в ChinaGuard!",
    )

    # Mark order as done
    await update_status(order_id, "done")
    await message.answer(f"Отчёт отправлен клиенту. Заявка #{order_id} закрыта.")
