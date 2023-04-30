import random

import json5 as json

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import hide_link

import classes

router = Router()

start_text = """
Это простой бот с довольно странным функционалом созданный по приколу ради опыта разработки ботов при помощи python + aiogram

Некоторая информация по командам:
/help - полный список команд
/info - инфа о боте и тд 
/meme - рандомный мем из коллекции (можно добавить свой)

Прошу сильно бота не пинать, у TelegramBotApi довольно сильные ограничения
30 сообщений в секунду всего
20 сообщений в одну группу в минуту
не больше 1 сообщения в секунду в 1 чат

"""


@router.message(Command("start"), F.text)
async def command_start(message: Message):
    user = classes.User(message.from_user)
    await message.reply(start_text)
