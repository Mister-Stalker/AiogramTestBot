import aiogram
import json5 as json

from aiogram import filters, types

import classes


class PermissionFilter(filters.BaseFilter):
    any_list: list
    all_list: list

    def __init__(self, any_list=None, all_list=None):
        self.any_list = any_list if any_list else ["default_true"]
        self.all_list = all_list if all_list else []

    async def __call__(self, message: types.Message, bot: aiogram.Bot):
        user = classes.User(message.from_user)
        return user.permissions.check_permissions_list_all(self.all_list) and \
            user.permissions.check_permissions_list_any(self.any_list)


class PermissionCommandFilter(PermissionFilter):
    def __init__(self, name: str):
        cfg = json.load(open("configs/commands.json5", encoding="utf-8"))
        super().__init__(any_list=cfg.get(name, {}).get("permissions", {}).get("any", None),
                         all_list=cfg.get(name, {}).get("permissions", {}).get("all", None),
                         )

