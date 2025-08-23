# database/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import MONGODB_URI

client = AsyncIOMotorClient(MONGODB_URI)
db = client['clash_bot_db']

players_collection = db['players']
leaderboard_snapshots_collection = db['leaderboard_snapshots']
