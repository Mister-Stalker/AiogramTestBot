# этот модуль называется help_handler а не просто help только из-за того что в python имя help занято

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"), F.text)
async def command_help(message: Message):
    text = (f"Список команд:\n"

            f"/help - помощь и подсказки\n"

            f"/start - старт бота\n"

            f"/info - информация о боте\n"

            f"/meme - рандомный мем из списка\n"

            f"/add_meme - добавить мем в список мемов (прошу не добавлять всякую ерунду)\n"

            f"/add_music_file - добавить музыкальный файл ("
            f"эта функция работает, но не полностью и по сути вообще не нужна, эти фалы нигде не используются, просто сохраняются, "
            f"это было сделано просто для изучения работы конечных автоматов\n"

            f"/test - первая команда в этом боте, выводит инфу о сообщении, чате и тд, просто для теста\n")
    await message.reply(text)
