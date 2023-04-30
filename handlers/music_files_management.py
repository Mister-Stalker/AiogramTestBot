from contextlib import suppress
from typing import BinaryIO

import aiogram
from aiogram import types, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

import filters
import classes.music_file

router = aiogram.Router()
router.message(filters.ChatIsPrivateFilter())


# Различные классы
class TagEditorCallback(CallbackData, prefix="add_tag"):
    action: str


def make_tag_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="изменить заголовок", callback_data=TagEditorCallback(action="change_title")
    )
    builder.button(
        text="изменить исполнителя", callback_data=TagEditorCallback(action="change_artist")
    )
    builder.button(
        text="изменить дату релиза", callback_data=TagEditorCallback(action="change_release_date")
    )
    builder.button(
        text="изменить путь", callback_data=TagEditorCallback(action="change_path")
    )
    builder.button(
        text="изменить имя файла", callback_data=TagEditorCallback(action="change_filename")
    )
    builder.button(
        text="Сохранить файл", callback_data=TagEditorCallback(action="save_file")
    )
    builder.button(
        text="Отменить", callback_data=TagEditorCallback(action="cancel")
    )
    # Выравниваем кнопки по 4 в ряд, чтобы получилось 4 + 1
    builder.adjust(1)
    return builder.as_markup()


class AddMusic(StatesGroup):
    input_title = State()
    input_artist = State()
    input_release_date = State()
    input_path = State()
    input_filename = State()
    wait_action = State()
    wait_file = State()


# Вспомогательные функции


def get_file_descr(file_data: dict):
    text = (f"Заголовок: {file_data['title']}\n"
            f"Исполнитель: {file_data['artist']}\n"
            f"Дата релиза: {file_data['release_date']}\n"
            f"Путь: {file_data['path']}\\{file_data['filename']}.{file_data['format']}\n")
    return text


async def update_music_file_text(state: FSMContext):
    with suppress(TelegramBadRequest):
        file_data = await state.get_data()
        await file_data["message"].edit_text(
            get_file_descr(file_data),
            reply_markup=make_tag_keyboard()
        )


async def start_edit_tag(message: types.Message, bot: aiogram.Bot, state: FSMContext):
    file = await bot.get_file(message.audio.file_id)

    file_format = message.audio.file_name.split(".")[-1]

    filename = ".".join(message.audio.file_name.split(".")[:-1])

    await state.update_data(file_path=file.file_path,
                            title="",
                            artist="",
                            release_date="",
                            path="",
                            filename=filename,
                            format=file_format, )
    await state.set_state(AddMusic.wait_action)
    file_data = await state.get_data()
    await message.reply(
        get_file_descr(file_data),
        reply_markup=make_tag_keyboard()
    )


# тут начинается описание логики бота


@router.message(Command("add_music_file"), filters.PermissionCommandFilter("add_music_file"), F.audio)
async def cmd_add_music_file(message: types.Message, bot: aiogram.Bot, state: FSMContext):
    # file_path = (await bot.get_file(message.audio.file_id)).file_path
    await start_edit_tag(message, bot, state)


@router.message(Command("add_music_file"), filters.PermissionCommandFilter("add_music_file"))
async def cmd_add_music_file_without_file(message: types.Message, bot: aiogram.Bot, state: FSMContext):
    # file_path = (await bot.get_file(message.audio.file_id)).file_path
    await state.set_state(AddMusic.wait_file)
    await message.answer("отправьте файл")


@router.message(F.audio, AddMusic.wait_file)
async def get_file_from_user(message: types.Message, bot: aiogram.Bot, state: FSMContext):
    await start_edit_tag(message, bot, state, )


@router.callback_query(TagEditorCallback.filter(F.action == "save_file"))
async def callback_save_file(
        callback: types.CallbackQuery,
        callback_data: TagEditorCallback,
        state: FSMContext,
        bot: aiogram.Bot,
):
    file_data = await state.get_data()
    _id = classes.MusicFile.add_file(artist=file_data["artist"],
                                     filename=file_data["filename"],
                                     file_format=file_data["format"],
                                     path=file_data["path"],
                                     title=file_data["title"],
                                     release_date=file_data["release_date"],
                                     )
    music_file = classes.MusicFile(_id)
    file: BinaryIO = await bot.download_file(file_data['file_path'])
    temp_filename = classes.music_file.fill_tag(file, music_file)
    print(temp_filename)
    await state.clear()
    sa = await callback.message.answer_audio(audio=types.FSInputFile(path=temp_filename,
                                                                     filename=f"{music_file.filename}.{music_file.format}"),
                                             performer=music_file.artist,
                                             title=music_file.title)
    music_file.file_id = sa.audio.file_id
    await callback.message.answer_audio(music_file.file_id)
    await callback.answer()


@router.callback_query(TagEditorCallback.filter(F.action == "cancel"))
async def callback_cancel(
        callback: types.CallbackQuery,
        callback_data: TagEditorCallback,
        state: FSMContext,
):
    await callback.answer("действие отменено")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.edit_text(callback.message.text + "\n(Отменено)")
    await state.clear()


# тут начинается обработка callback и сообщений для изменения тэга


@router.callback_query(TagEditorCallback.filter(F.action == "change_title"))
async def callback_change_title(
        callback: types.CallbackQuery,
        callback_data: TagEditorCallback,
        state: FSMContext,
):
    await callback.answer()
    await callback.message.answer("Введите название")
    await state.update_data(message=callback.message)
    await state.set_state(AddMusic.input_title)


@router.callback_query(TagEditorCallback.filter(F.action == "change_artist"))
async def callback_change_artist(
        callback: types.CallbackQuery,
        callback_data: TagEditorCallback,
        state: FSMContext,
):
    await callback.answer()
    await callback.message.answer("Введите имя Исполнителя")
    await state.update_data(message=callback.message)
    await state.set_state(AddMusic.input_artist)


@router.callback_query(TagEditorCallback.filter(F.action == "change_release_date"))
async def callback_change_release_date(
        callback: types.CallbackQuery,
        callback_data: TagEditorCallback,
        state: FSMContext,
):
    await callback.answer()
    await callback.message.answer("Введите дату релиза")
    await state.update_data(message=callback.message)
    await state.set_state(AddMusic.input_release_date)


@router.callback_query(TagEditorCallback.filter(F.action == "change_path"))
async def callback_change_path(
        callback: types.CallbackQuery,
        callback_data: TagEditorCallback,
        state: FSMContext,
):
    await callback.answer()
    await callback.message.answer("Введите путь для файла (для разделения папок используйте точку)")
    await state.update_data(message=callback.message)
    await state.set_state(AddMusic.input_path)


@router.callback_query(TagEditorCallback.filter(F.action == "change_filename"))
async def callback_change_path(
        callback: types.CallbackQuery,
        callback_data: TagEditorCallback,
        state: FSMContext,
):
    await callback.answer()
    await callback.message.answer("Введите имя файла (без расширения)")
    await state.update_data(message=callback.message)
    await state.set_state(AddMusic.input_filename)


@router.message(F.text, AddMusic.input_title, filters.TextInputFilterOnlyText())
async def input_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddMusic.wait_action)
    await update_music_file_text(state)


@router.message(F.text, AddMusic.input_artist, filters.TextInputFilterOnlyText())
async def input_artist(message: types.Message, state: FSMContext):
    await state.update_data(artist=message.text)
    await state.set_state(AddMusic.wait_action)
    await update_music_file_text(state)


@router.message(F.text,
                AddMusic.input_release_date,
                filters.TextInputFilterOnlyText(),
                )
async def input_release_date(message: types.Message, state: FSMContext):
    await state.update_data(release_date=message.text)
    await state.set_state(AddMusic.wait_action)
    await update_music_file_text(state)


@router.message(F.text,
                AddMusic.input_path,
                filters.TextInputRegexFilter(pattern=r"[\w\s.]+",
                                             text=filters.TextInputFilterOnlyText.on_false_text),
                )
async def input_path(message: types.Message, state: FSMContext):
    text = message.text.replace(".", "\\")
    await state.update_data(path=text)
    await state.set_state(AddMusic.wait_action)
    await update_music_file_text(state)


@router.message(F.text, AddMusic.input_filename, filters.TextInputFilterOnlyText())
async def input_path(message: types.Message, state: FSMContext):
    await state.update_data(filename=message.text)
    await state.set_state(AddMusic.wait_action)
    await update_music_file_text(state)
