from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import classes
import filters

router = Router()


class InfoCommandCallbackData(CallbackData, prefix="info"):
    data: str


def info_keyboard() -> InlineKeyboardMarkup:
    """
        создание клавиатуры
        :return:
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="информация о разработчике", callback_data=InfoCommandCallbackData(data="about_dev")
    )

    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("info"),
                filters.ChatIsPrivateFilter(),
                F.text, )
async def command_info(message: Message):
    user = classes.User(message.from_user)
    text = (f"Бот для телеграмма созданный по приколу и для тренировки\n"
            f"Разработчик: @Mister_Stalker \n"
            f"Бот сделан при помощи Aiogram, также для базы данных (MongoDB) используется pymongo\n"
            f"Версия python: 3.11\n"
            f"ссылка на github: https://github.com/Mister-Stalker/AiogramTestBot"
            )
    await message.reply(text, reply_markup=info_keyboard())


@router.callback_query(InfoCommandCallbackData.filter(F.data == "about_dev"))
async def callback_change_text(
        callback: types.CallbackQuery, ) -> None:
    await callback.answer()
    text = (f"Тут должна быть инфа о разработчике, "
            f"когда-нибудь она здесь точно будет")
    await callback.message.answer(text)
