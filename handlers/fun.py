import random

import json5 as json

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.markdown import hide_link

router = Router()


@router.message(Command("meme"), F.text)
async def send_meme(message: Message):
    meme = random.choice(json.load(open("configs/memes.json5", encoding="utf-8")))
    text = meme["text"] if isinstance(meme["text"], str) else "".join(meme["text"])
    text = hide_link(meme.get("link", "")) + text
    text += f"\n({meme.get('id', '-0')})"
    # text += f"\n({t})" if (t := meme.get('id', None)) is None else ""
    await message.answer(text)
