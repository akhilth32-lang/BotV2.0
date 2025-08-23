from bson import ObjectId
from database.database import get_collection

players_col = get_collection("players")

def create_player(player_data: dict) -> str:
    """Insert a new player record."""
    result = players_col.insert_one(player_data)
    return str(result.inserted_id)

def get_player_by_tag(tag: str) -> dict:
    """Retrieve a player by their Clash of Clans tag."""
    return players_col.find_one({"tag": tag})

def update_player_by_tag(tag: str, update_data: dict) -> int:
    """Update player data by tag. Returns number of modified documents."""
    result = players_col.update_one({"tag": tag}, {"$set": update_data})
    return result.modified_count

def delete_player_by_tag(tag: str) -> int:
    """Delete a player by tag. Returns number of deleted documents."""
    result = players_col.delete_one({"tag": tag})
    return result.deleted_count
    
