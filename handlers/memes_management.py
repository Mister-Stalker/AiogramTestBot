from contextlib import suppress
import json5 as json

import aiogram
from aiogram import types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hide_link

import filters

router = aiogram.Router()
router.message(filters.ChatIsPrivateFilter())  # все команды работают только в приватных чатах


class MemeEditorCallback(CallbackData, prefix="meme_editor"):
    action: str


class AddMeme(StatesGroup):
    input_text = State()
    input_url = State()
    wait_action = State()


def meme_edit_keyboard() -> InlineKeyboardMarkup:
    """
    создание клавиатуры для редактирования мема
    :return:
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="изменить текст", callback_data=MemeEditorCallback(action="change_text")
    )
    builder.button(
        text="изменить ссылку на картинку", callback_data=MemeEditorCallback(action="change_link")
    )
    builder.button(
        text="Сохранить Мем", callback_data=MemeEditorCallback(action="save_meme")
    )
    builder.button(
        text="Отменить", callback_data=MemeEditorCallback(action="cancel")
    )
    builder.adjust(1)
    return builder.as_markup()


# Вспомогательные функции


async def update_meme_message(state: FSMContext) -> None:
    """
    обновить сообщение с редактируемым мемом
    :param state: текущий state
    :return:
    """
    with suppress(TelegramBadRequest):
        meme_data = await state.get_data()
        print(meme_data)
        await meme_data["message"].edit_text(
            text=f"{hide_link(meme_data['link']) if meme_data['link'] else ''}"
                 f"{meme_data['text']}",
            reply_markup=meme_edit_keyboard()
        )


async def start_add_meme(message: types.Message,
                         bot: aiogram.Bot,
                         state: FSMContext,
                         text: str = "default_text",
                         link: str = "",
                         ) -> None:
    """
    запуск редактора мема
    :param message: сообщение вызывающее цепочку команд
    :param bot: объект бота
    :param state: стейт
    :param text: текст мема (по умолчанию постой)
    :param link: ссылка на картинку мема (по умолчанию пустая)
    :return:
    """
    await state.update_data(link=link, text=text)
    await state.set_state(AddMeme.wait_action)
    meme_data = await state.get_data()
    mess = await message.reply(
        text=f"{hide_link(meme_data['link']) if meme_data['link'] else ''}"
             f"{meme_data['text']}",
        reply_markup=meme_edit_keyboard()
    )

    await state.update_data(message=mess)


@router.message(Command("add_meme"),
                filters.HasArgsFilter(),
                filters.TextInputRegexFilter(r"[\w\s*.,:;()]+", is_command=True),
                )
async def add_meme_command(message: types.Message, bot: aiogram.Bot, state: FSMContext):
    await start_add_meme(message, bot, state, text=" ".join(message.text.split()[1:]))


@router.message(Command("add_meme"))
async def add_meme_command_without_text(message: types.Message, bot: aiogram.Bot, state: FSMContext):
    await start_add_meme(message, bot, state)


@router.callback_query(MemeEditorCallback.filter(F.action == "cancel"))
async def callback_cancel(
        callback: types.CallbackQuery,
        callback_data: MemeEditorCallback,
        state: FSMContext, ) -> None:
    await callback.answer("действие отменено")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(callback.message.text + "\n(Отменено)")
    await state.clear()


@router.callback_query(MemeEditorCallback.filter(F.action == "save_meme"))
async def callback_save_meme(
        callback: types.CallbackQuery,
        callback_data: MemeEditorCallback,
        state: FSMContext, ) -> None:
    await callback.answer("мем сохранён")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(callback.message.text + "\n(saved)")
    meme_data = await state.get_data()
    await state.clear()
    cfg = json.load(open("configs/memes.json5", encoding="utf-8"))
    meme_id = max(cfg, key=lambda m: m.get("id", 0)).get("id", 0) + 1
    cfg.append({
        "id": meme_id,
        "text": meme_data["text"],
        "link": meme_data["link"],
    })
    print(cfg[-1])
    json.dump(cfg, open("configs/memes.json5", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    await callback.message.answer("мем сохранен\n"
                                  f"id мема: {meme_id} (id нужен для редактирования или удаления)")


@router.callback_query(MemeEditorCallback.filter(F.action == "change_text"))
async def callback_change_text(
        callback: types.CallbackQuery,
        callback_data: MemeEditorCallback,
        state: FSMContext, ) -> None:
    await callback.answer()
    await callback.message.answer("напишите текст мема")
    await state.set_state(AddMeme.input_text)


@router.callback_query(MemeEditorCallback.filter(F.action == "change_link"))
async def callback_change_link(
        callback: types.CallbackQuery,
        callback_data: MemeEditorCallback,
        state: FSMContext, ) -> None:
    await callback.answer()
    await callback.message.answer("отправьте ссылку на картинку для мема")
    await state.set_state(AddMeme.input_url)


@router.message(F.text,
                AddMeme.input_text,
                filters.TextInputRegexFilter(r"[\w\s*.,:;()]+", send_default_text=True),
                )
async def input_text(message: types.Message,
                     state: FSMContext, ) -> None:
    await state.update_data(text=message.text)
    print(await state.get_data())
    await state.set_state(AddMeme.wait_action)
    await update_meme_message(state)


@router.message(F.text, AddMeme.input_url, filters.HasUrlFilter())
async def input_url(message: types.Message,
                    state: FSMContext,
                    url: str, ) -> None:
    await state.update_data(link=url)
    await state.set_state(AddMeme.wait_action)
    await update_meme_message(state)
