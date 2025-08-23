from pymongo import MongoClient
from config.settings import MONGO_URI

mongo_client = MongoClient(MONGO_URI)
db = mongo_client['clash_bot']

def get_collection(collection_name: str):
    return db[collection_name]
  
