import aiogram
from aiogram import F
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("download_music_file"), F.audio, lambda m: m.audio.file_name.endswith(".mp3"))
async def test_music_file(message: Message, bot: aiogram.Bot):
    await message.answer(f"i get a Audio: {message.audio}")
    await bot.download_file((await bot.get_file(message.audio.file_id)).file_path,
                            f"C:/Users/pna24/Downloads/[bot_downloaded] {message.audio.file_name}")


@router.message(Command("download_music_file"), F.audio)
async def test_music_file(message: Message):
    await message.answer("i need a .mp3 file!!!")


@router.message(Command("download_music_file"), F.photo)
async def test_music_file(message: Message):
    await message.answer("i get a photo, it is not music file")


@router.message(Command("download_music_file"), F.text)
async def test_music_file(message: Message):
    await message.answer("i get a text message, not a music file")
