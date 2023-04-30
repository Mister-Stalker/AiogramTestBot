import aiogram
from aiogram import F
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

import classes
import filters.chat_type

router = Router()


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
