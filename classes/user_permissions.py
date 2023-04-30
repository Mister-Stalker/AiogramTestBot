import pymongo.collection
from bson import ObjectId


class UserPermissions:
    """
    Класс для обработки прав пользователей
    user.permissions: {
        "key_1": True,
        "key_2": False
    }  - user has "key_1" permission and has not "key_2" and "key_3" permissions
    """

    __slots__ = [
        "_collection",
        "_id",
    ]

    def __init__(self, collection: pymongo.collection.Collection, _id: ObjectId) -> None:
        self._collection = collection
        self._id = _id

    @property
    def data(self) -> dict:
        return self._collection.find_one({"_id": self._id})

    @property
    def permissions_list(self):
        return self.data.get("permissions", {})

    def check_permission(self, name: str) -> bool:
        """
        Проверка имеет ли пользователь разрешение
        :param name:
        :return:
        """
        return self.permissions_list.get(name, False)

    def check_permissions_list_any(self, lst: list[str]) -> bool:
        """
        True если пользователь имеет хотя бы одно право из списка
        :param lst:
        :return:
        """
        return True if "default_true" in lst else any([self.check_permission(name) for name in lst])

    def check_permissions_list_all(self, lst: list[str]) -> bool:
        """
        True если пользователь имеет все права из списка
        :param lst:
        :return:
        """
        return all([self.check_permission(name) for name in lst])
