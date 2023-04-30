import datetime
import os
from typing import BinaryIO

from bson import ObjectId
import mutagen
from mutagen import id3
from mutagen.easyid3 import EasyID3

import classes
import classes.collections
from classes import db_handler

file_mask = {
    "title": "",
    "artist": "",
    "add_date": datetime.datetime.now(),
    "release_date": None,
    "file_id": 0,
    "file_path": "",
    "path": "",
    "filename": "",
    "format": "",

}


class MusicFile(db_handler.DataBaseHandler):
    def __init__(self, _id: ObjectId | str):
        self.id = ObjectId(_id)
        self.collection = classes.collections.get_collection(self.__class__.__name__)
        super().__init__(self.collection, self.id)
        if not self.dict:
            raise FileNotFoundError

    @property
    def title(self):
        return self["title"]

    @title.setter
    def title(self, val):
        self["title"] = val

    @property
    def artist(self):
        return self["artist"]

    @artist.setter
    def artist(self, val):
        self["artist"] = val

    @property
    def file_id(self):
        return self["file_id"]

    @file_id.setter
    def file_id(self, val):
        self["file_id"] = val

    @property
    def file_path(self):
        return self["file_path"]

    @property
    def filename(self):
        return self["filename"]

    @file_path.setter
    def file_path(self, val):
        self["file_path"] = val

    @property
    def format(self):
        return self["format"]

    @property
    def path(self):
        return self["path"]

    @classmethod
    def add_file(cls, file_path=None, artist=None, title=None, release_date=None, path="", filename="", file_format=""):
        new_file = file_mask.copy()
        new_file["file_path"] = file_path
        new_file["artist"] = artist
        new_file["title"] = title
        new_file["release_date"] = release_date
        new_file["add_date"] = datetime.datetime.now()
        new_file["path"] = path
        new_file["filename"] = filename
        new_file["format"] = file_format

        collection = classes.collections.get_collection(cls.__name__)
        res = collection.insert_one(new_file)

        return res.inserted_id

    @classmethod
    def get_files_list(cls) -> list:
        collection = classes.collections.get_collection(cls.__name__)
        return [cls(obj["_id"]) for obj in collection.find()]

    @classmethod
    def find_by_title(cls, title: str):
        return list(filter(lambda x: title.lower() in x.title.lower(), cls.get_files_list()))

    @classmethod
    def find_by_artist(cls, artist: str):
        return list(filter(lambda x: artist.lower() in x.artist.lower(), cls.get_files_list()))


def fill_tag(file: BinaryIO, music_file: MusicFile):
    # if not os.path.exists(os.getcwd()+f"\\temp\\{music_file.path}"):
    #     os.makedirs(os.getcwd()+f"\\temp\\{music_file.path}")
    temp_filename = os.getcwd()+f"\\temp\\{music_file.id}.{music_file.format}"
    with open(temp_filename, "wb") as f:
        f.write(file.read())
    try:
        audio_file = EasyID3(temp_filename)
    except id3.ID3NoHeaderError:
        audio_file = mutagen.File(temp_filename, easy=True)
        audio_file.add_tags()
    audio_file["artist"] = music_file.artist
    audio_file.save()

    return temp_filename
