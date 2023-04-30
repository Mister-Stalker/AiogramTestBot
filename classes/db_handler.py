import json5 as json
import operator
from functools import reduce
from typing import Any
import pymongo
from bson import ObjectId


def update_dict(item: dict, mask: dict) -> dict:
    """
    добавление в словарь item полей из mask если их там нет
    :param item:
    :param mask:
    :return:
    """
    edited_item = mask | item

    for p in edited_item.keys():
        if type(edited_item[p]) == dict:
            edited_item[p] = mask[p] | edited_item[p]
            for q in edited_item[p].keys():
                if type(edited_item[p][q]) == dict:
                    edited_item[p][q] = mask[p][q] | edited_item[p][q]

    return edited_item


class DataBaseHandlerMongoDB:
    """
    Обработчик базы данных mongodb
    позволяет быстро получать доступ к данным и быстро их изменять
    доступ ко вложенным словарям выполняется так:
    {
        "a": {"b": 1, "c": 2}
    }

    object["a.b"] что бы получить значение
    object["a.b"] = 10 что бы установить значение (изменение напрямую в бд!)
    ключи во всех словарях не должны иметь "."
    """

    def __init__(self, collection: pymongo.collection.Collection, _id: ObjectId | str) -> None:
        """

        :param collection: коллекция бд
        :param _id: _id объекта с которым надо работать
        """
        self._id = (ObjectId(_id))
        self._collection = collection

    @property
    def dict(self) -> dict:
        """
        Возвращает словарь из бд
        :return:
        """
        return self._collection.find_one({"_id": self._id})

    def _update(self, key: str, value: Any) -> None:
        self._collection.update_one({"_id": self._id}, {'$set': {key: value}})

    def update_db(self, mask: dict):
        self._collection.replace_one({"_id": self._id}, update_dict(self.dict, mask))

    def __getitem__(self, item: str) -> Any:
        items = item.split(".")
        return reduce(operator.getitem, items, self.dict)

    def __setitem__(self, key: str, value: Any) -> None:
        self._update(key, value)

    def get(self, key: str) -> Any:
        return self.__getitem__(key)

    def add(self,
            key,
            value,
            check_zero=False,
            limit_max=None,
            limit_min=None) -> None:
        """
        увеличить значение на value
        :param key: ключ
        :param value:
        :param check_zero: нужно ли проверить значение на то что оно меньше 0
        :param limit_max: максимальный лимит значения
        :param limit_min: минимальный лимит значения
        :return:
        """
        self[key] = self[key] + value
        if check_zero:
            if self[key] < 0:
                self[key] = 0
        if limit_max:
            if self[key] > limit_max:
                self[key] = limit_max
        if limit_min:
            if self[key] < limit_min:
                self[key] = limit_min

    def deduct(self,
               key,
               value,
               check_zero=True,
               limit_max=None,
               limit_min=None) -> None:
        """
        уменьшить значение на value
        :param value:
        :param key: ключ
        :param check_zero: нужно ли проверить значение на то что оно меньше 0
        :param limit_max: максимальный лимит значения
        :param limit_min: минимальный лимит значения
        :return:
        """
        self[key] = self[key] - value
        if check_zero:
            if self[key] < 0:
                self[key] = 0
        if limit_max:
            if self[key] > limit_max:
                self[key] = limit_max
        if limit_min:
            if self[key] < limit_min:
                self[key] = limit_min

    def set(self, key, value,
            check_zero=False,
            limit_max=None,
            limit_min=None) -> None:
        """
        установить значение на value
        :param key: ключ
        :param value:
        :param check_zero: нужно ли проверить значение на то что оно меньше 0
        :param limit_max: максимальный лимит значения
        :param limit_min: минимальный лимит значения
        :return:
        """
        self[key] = value
        if check_zero:
            if self[key] < 0:
                self[key] = 0
        if limit_max:
            if self[key] > limit_max:
                self[key] = limit_max
        if limit_min:
            if self[key] < limit_min:
                self[key] = limit_min


class DictParser:

    def __init__(self, d: dict):
        self.dict = d

    def __getitem__(self, item: str) -> Any:
        items = item.split(".")
        return reduce(operator.getitem, items, self.dict)

    def __setitem__(self, key: str, value: Any) -> None:
        last_key = key.split(".")[-1]
        if last_key.startswith("|"):
            if last_key[1:].isdigit():
                last_key = int(last_key[1:])
        self[".".join(key.split(".")[:-1])][last_key] = value


class JSONParser:

    def __init__(self, path: str, default_first_key="parameters"):
        self.path: str = path
        self.dict: dict = json.load(open(path, encoding="utf-8"))
        self._default_first_key = default_first_key

    def _update_json_file(self):
        json.dump(self.dict, open(self.path, "w", encoding="utf-8"), indent=4, ensure_ascii=False)

    def __getitem__(self, item: str) -> Any:
        items = list(item.split("."))
        if items[0] not in self.dict.keys():
            items.insert(0, self._default_first_key)
        for i in range(len(items)):
            if items[i].startswith("|"):
                if items[i][1:].isdigit():
                    items[i] = int(items[i][1:])
        return reduce(operator.getitem, items, self.dict)

    def __setitem__(self, key: str, value: Any) -> None:
        if len(key.split(".")) > 1:
            last_key = key.split(".")[-1]
            if last_key.startswith("|"):
                if last_key[1:].isdigit():
                    last_key = int(last_key[1:])
            self[".".join(key.split(".")[:-1])][last_key] = value
        else:
            self.dict[key] = value
        self._update_json_file()

    def get(self, key: str, default_value: Any):
        # print(key)
        if len(key.split(".")) == 1:
            if key not in self.dict.keys():
                self[key] = default_value
            return self[key]
        if key.split(".")[-1] not in self[".".join(key.split(".")[0:-1])].keys():
            self[key] = default_value
            self._update_json_file()

        return self[key]


DataBaseHandler = DataBaseHandlerMongoDB
