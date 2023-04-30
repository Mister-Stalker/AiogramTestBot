import pymongo

DATABASE_NAME = "AiogramTestBot"


def get_collection(class_name: str)->pymongo.collection.Collection:
    client = pymongo.MongoClient("localhost", 27017)
    collection = None
    match class_name.lower():
        case "user" | "users":
            collection = client[DATABASE_NAME]["users"]
        case "musicfile" | "music_file":
            collection = client[DATABASE_NAME]["music_files"]

    return collection
