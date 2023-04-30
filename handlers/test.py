import pprint
from contextlib import suppress
from typing import Optional

import aiogram
from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F
from aiogram import html
import classes
import filters.chat_type

user_data = {}
router = Router()


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int]


def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="-2", callback_data=NumbersCallbackFactory(action="change", value=-2)
    )
    builder.button(
        text="-1", callback_data=NumbersCallbackFactory(action="change", value=-1)
    )
    builder.button(
        text="+1", callback_data=NumbersCallbackFactory(action="change", value=1)
    )
    builder.button(
        text="+2", callback_data=NumbersCallbackFactory(action="change", value=2)
    )
    builder.button(
        text="Подтвердить", callback_data=NumbersCallbackFactory(action="finish")
    )
    # Выравниваем кнопки по 4 в ряд, чтобы получилось 4 + 1
    builder.adjust(4)
    return builder.as_markup()


async def update_num_text_fab(message: types.Message, new_value: int):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"Укажите число: {new_value}",
            reply_markup=get_keyboard_fab()
        )


# Нажатие на одну из кнопок: -2, -1, +1, +2
@router.callback_query(NumbersCallbackFactory.filter(F.action == "change"))
async def callbacks_num_change_fab(
        callback: types.CallbackQuery,
        callback_data: NumbersCallbackFactory
):
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, 0)

    user_data[callback.from_user.id] = user_value + callback_data.value
    await update_num_text_fab(callback.message, user_value + callback_data.value)
    await callback.answer()


# Нажатие на кнопку "подтвердить"
@router.callback_query(NumbersCallbackFactory.filter(F.action == "finish"))
async def callbacks_num_finish_fab(callback: types.CallbackQuery):
    # Текущее значение
    user_value = user_data.get(callback.from_user.id, 0)

    await callback.message.edit_text(f"Итого: {user_value}")
    await callback.answer()


@router.message(Command("numbers_fab"))
async def cmd_numbers_fab(message: types.Message):
    user_data[message.from_user.id] = 0
    await message.answer("Укажите число: 0", reply_markup=get_keyboard_fab())


@router.message(Command("test"), F.text, filters.ChatTypeFilter(["group", "supergroup"]))
async def cmd_test_public(message: Message, command: CommandObject):
    await message.answer(
        f"Public version\n"
        f"Chat:\n"
        f"chat id: {message.chat.id}\n"
        f"chat title: {message.chat.title}\n"
        f"chat type: {message.chat.type}\n"
        f"chat full name: {message.chat.full_name}\n"
        f"chat is forum: {message.chat.is_forum}\n\n"
        f'forum_topic_closed: {message.forum_topic_closed}\n'
        f'forum_topic_created: {message.forum_topic_created}\n'
        f'forum_topic_edited: {message.forum_topic_edited}\n'
        f'forum_topic_reopened: {message.forum_topic_reopened}\n'
        f'general_forum_topic_hidden: {message.general_forum_topic_hidden}\n'
        f'general_forum_topic_unhidden: {message.general_forum_topic_unhidden}\n'
        f"message_thread_id: {message.message_thread_id}\n"


        f"\nArgs:\n"
        f"args: {command.args}\n\n"
        f"Message:\n"
        f"message id: {message.message_id}\n"
        f"message text: {message.text}\n"
        f"channel chat created: {message.channel_chat_created}\n\n"

        f"User:\n"
        f"user id: {message.from_user.id}\n"
        f"username: {message.from_user.username}\n"
        f"full name: {message.from_user.full_name}\n"
        f"language code: {message.from_user.language_code}\n"

    )


@router.message(Command("test"), F.text, filters.ChatTypeFilter("private"))
async def cmd_test_private(message: Message, command: CommandObject, bot: aiogram.Bot):
    user = classes.User(message.from_user)
    await message.answer(
        f"private version\n"
        f"chat id: {message.chat.id}\n"
        f"chat username: {message.chat.username}\n"
        f"chat type: {message.chat.type}\n"
        f"chat full_name: {message.chat.full_name}\n\n"

        f"args: {command.args}\n\n"

        f"message id: {message.message_id}\n"
        f"message text: {message.text}\n"
        f"channel chat created: {message.channel_chat_created}\n\n"

        f"user id: {message.from_user.id}\n"
        f"username: {message.from_user.username}\n"
        f"full name: {message.from_user.full_name}\n"
        f"language code: {message.from_user.language_code}\n"

        f"\nCustom User\n"
        f"fullname: {await user.get_fullname(message.chat.id, bot)}\n"
        f"username: {await user.get_username(message.chat.id, bot)}\n"
        f"for search: {await user.get_fullname_and_username(message.chat.id, bot)}\n"

    )


@router.message(Command("user_data"), filters.ChatIsPrivateFilter())
async def cmd_user_data_private(message: Message):
    user = classes.User(message.from_user.id)
    user.update_db()
    await message.answer(f"{html.code(pprint.pformat(user.dict, width=10))}")


@router.message(Command("user_data"), filters.ChatIsGroupFilter())
async def cmd_user_data_public(message: Message):
    user = classes.User(message.from_user.id)
    user.update_db()
    await message.answer("Эта команда доступна только в ЛС бота")
