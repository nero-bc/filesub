from pymongo import MongoClient

from FSub import DATABASE_URL, DATABASE_NAME, LOGGER

dbclient  = MongoClient(DATABASE_URL)
database  = dbclient[DATABASE_NAME]

user_data = database['users']


def add_user(user_id: int):
    if not user_data.find_one({'_id': user_id}):
        user_data.insert_one({'_id': user_id})
        LOGGER.info(f"{user_id} ditambahkan ke database.")
    else: return None


def full_user():
    users   = user_data.find()
    user_id = [user['_id'] for user in users]
    return user_id


def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})
    LOGGER.info(f"{user_id} dihapus dari database.")
    return