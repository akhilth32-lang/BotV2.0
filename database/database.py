# database/database.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["coc_bot"]

players_col = db["players"]
backup_col = db["backup_players"]

# Ensure indexes for performance
players_col.create_index([("trophies", -1)])
players_col.create_index([("player_tag", 1)])
players_col.create_index([("discord_id", 1)])
