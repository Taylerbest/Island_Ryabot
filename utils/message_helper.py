# utils/message_helper.py

from aiogram.types import Message, CallbackQuery
from typing import Union


async def send_formatted(
        obj: Union[Message, CallbackQuery],
        text: str,
        reply_markup=None,
        edit: bool = False
):
    """
    Универсальная функция для отправки сообщений с правильной разметкой.
    Исправляет проблему с отображением *жирного текста*.

    Как использовать:
        await send_formatted(message, "Привет!", reply_markup=keyboard)
        await send_formatted(callback, "Текст", edit=True)
    """

    # Отправка через CallbackQuery (когда нажали кнопку)
    if isinstance(obj, CallbackQuery):
        if edit:
            await obj.message.edit_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await obj.message.answer(
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

    # Отправка через Message (когда написали команду)
    elif isinstance(obj, Message):
        await obj.answer(
            text=text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
