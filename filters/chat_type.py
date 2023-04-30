from aiogram import filters, types


class ChatTypeFilter(filters.BaseFilter):
    def __init__(self, chat_type: str | list):
        self.chat_type = chat_type

    async def __call__(self, message: types.Message):
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class ChatIsGroupFilter(filters.BaseFilter):
    def __init__(self, is_group: bool = True):
        self.is_group = is_group

    async def __call__(self, message: types.Message):
        if self.is_group:
            return message.chat.type in ("group", "supergroup")
        else:
            return message.chat.type in ("private",)


class ChatIsPrivateFilter(ChatIsGroupFilter):
    def __init__(self, is_private: bool = True):
        super().__init__(is_group=not is_private)
