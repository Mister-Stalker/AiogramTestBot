import asyncio

import json5 as json
import aiogram

import configs_reader
from handlers import fun, test, music_files_management, memes_management, start, info, help_handler


async def setup_commands(bot: aiogram.Bot):
    await bot.set_my_commands([aiogram.types.BotCommand(command=command["command"], description=command["description"])
                               for _, command in json.load(open("configs/commands.json5", encoding="utf-8")).items()])


async def start_bot():
    bot = aiogram.Bot(token=configs_reader.config.bot_token.get_secret_value(),
                      parse_mode="HTML")
    dp = aiogram.Dispatcher()
    dp.include_routers(
        start.router,
        info.router,
        help_handler.router,
        fun.router,
        test.router,
        memes_management.router,
        music_files_management.router,
    )
    await setup_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def main():
    asyncio.run(start_bot())
