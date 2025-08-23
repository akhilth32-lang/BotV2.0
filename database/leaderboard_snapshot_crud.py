# database/leaderboard_snapshot_crud.py

from .database import leaderboard_snapshots_collection
import datetime

async def save_daily_snapshot(season: int, day: int, leaderboard_data: list):
    """Save a snapshot of leaderboard data for a given season and day."""
    snapshot_doc = {
        "season": season,
        "day": day,
        "leaderboard_data": leaderboard_data,
        "timestamp": datetime.datetime.utcnow()
    }
    await leaderboard_snapshots_collection.insert_one(snapshot_doc)
    return snapshot_doc

async def get_snapshot(season: int, day: int):
    """Retrieve a snapshot for a given season and day."""
    snapshot = await leaderboard_snapshots_collection.find_one({
        "season": season,
        "day": day
    })
    return snapshot
