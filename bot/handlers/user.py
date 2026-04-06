from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.config import ADMIN_ID
from bot.db import create_order

router = Router(name="user")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Добро пожаловать в ChinaGuard.\n"
        "Отправьте договор или опишите ситуацию — мы проверим риски по ГК КНР."
    )


@router.message(F.document)
async def handle_document(message: Message) -> None:
    doc = message.document
    order_id = await create_order(
        user_id=message.from_user.id,
        username=message.from_user.username,
        file_id=doc.file_id,
        file_name=doc.file_name,
    )
    await message.answer(
        f"Документ получен. Заявка #{order_id} создана.\n"
        "Наш специалист проверит его и свяжется с вами."
    )
    # Notify admin
    await message.forward(chat_id=ADMIN_ID)
    await message.bot.send_message(
        ADMIN_ID,
        f"📄 Новая заявка #{order_id}\n"
        f"От: @{message.from_user.username or 'N/A'} (ID: {message.from_user.id})\n"
        f"Файл: {doc.file_name}",
    )


@router.message(F.photo)
async def handle_photo(message: Message) -> None:
    photo = message.photo[-1]  # largest resolution
    order_id = await create_order(
        user_id=message.from_user.id,
        username=message.from_user.username,
        file_id=photo.file_id,
        file_name="photo.jpg",
    )
    await message.answer(
        f"Фото получено. Заявка #{order_id} создана.\n"
        "Наш специалист проверит его и свяжется с вами."
    )
    # Notify admin
    await message.forward(chat_id=ADMIN_ID)
    await message.bot.send_message(
        ADMIN_ID,
        f"📷 Новая заявка #{order_id} (фото)\n"
        f"От: @{message.from_user.username or 'N/A'} (ID: {message.from_user.id})",
    )


@router.message(F.text)
async def handle_text(message: Message) -> None:
    order_id = await create_order(
        user_id=message.from_user.id,
        username=message.from_user.username,
        description=message.text,
    )
    await message.answer(
        f"Описание получено. Заявка #{order_id} создана.\n"
        "Наш специалист рассмотрит вашу ситуацию и свяжется с вами."
    )
    # Notify admin
    await message.bot.send_message(
        ADMIN_ID,
        f"💬 Новая заявка #{order_id}\n"
        f"От: @{message.from_user.username or 'N/A'} (ID: {message.from_user.id})\n"
        f"Текст: {message.text[:200]}",
    )
