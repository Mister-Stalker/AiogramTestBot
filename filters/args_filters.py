from typing import Union, Any

from aiogram import filters, types


class HasArgsFilter(filters.BaseFilter):
    async def __call__(self, message: types.Message):
        if len(message.text.split(" ")) > 1:
            return True
        return False


class HasUrlFilter(filters.BaseFilter):
    async def __call__(self, message: types.Message) -> Union[bool, dict[str, Any]]:
        lst = list(filter(lambda e: e.type == "url", message.entities))
        if len(lst) > 0:
            return {"url": lst[0].extract_from(message.text)}
        return False
