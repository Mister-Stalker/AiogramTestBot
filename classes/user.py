import aiogram.types
import pymongo.collection

from classes import db_handler, collections, user_permissions

user_json = {
    "id": -1,
    "permissions": {
        "default_true": True,
        "default_false": False,
    },
}


class User(db_handler.DataBaseHandler):
    id: int

    def __init__(self, data):

        if isinstance(data, aiogram.types.User):
            self.id = data.id
        elif isinstance(data, (str, int)):
            self.id = int(data)
        else:
            raise ValueError

        self.collection: pymongo.collection.Collection = collections.get_collection(self.__class__.__name__)
        if not (self.collection.find_one({"id": self.id})):
            self.create_new_user(telegram_id=self.id)
        self._id = self.collection.find_one({"id": self.id})["_id"]
        super().__init__(self.collection, self._id)
        self.permissions = user_permissions.UserPermissions(collection=self.collection, _id=self._id)

    def update_db(self, **kwargs):
        super().update_db(user_json)

    @classmethod
    def create_new_user(cls, telegram_id: int):
        new_user_json = user_json.copy()
        new_user_json["id"] = telegram_id
        collection = collections.get_collection(cls.__name__)
        collection.insert_one(new_user_json)

    async def get_user(self, chat_id: int, bot: aiogram.Bot) -> aiogram.types.User:
        return (await bot.get_chat_member(chat_id, self.id)).user

    async def get_fullname(self, chat_id: int, bot: aiogram.Bot):
        return (await self.get_user(chat_id, bot)).full_name

    async def get_username(self, chat_id: int, bot: aiogram.Bot):
        return (await self.get_user(chat_id, bot)).username

    async def get_fullname_and_username(self, chat_id: int, bot: aiogram.Bot):
        user = (await self.get_user(chat_id, bot))
        return f"{user.full_name} ({user.username})"
