# apis/coc_api.py
import aiohttp
import os

COC_API_TOKEN = os.getenv("COC_API_TOKEN")  # Make sure this env var is set

API_BASE_URL = "https://api.clashofclans.com/v1"

headers = {
    "Authorization": f"Bearer {COC_API_TOKEN}"
}

async def fetch_player_data(session: aiohttp.ClientSession, player_tag: str):
    """
    Fetch player data from official Clash of Clans API by player tag.
    Returns player data dict or None on failure.
    """
    # Tags should start with '#'
    if not player_tag.startswith("#"):
        player_tag = "#" + player_tag
    # encode '#' properly for URL
    encoded_tag = player_tag.replace("#", "%23")

    url = f"{API_BASE_URL}/players/{encoded_tag}"
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return data
            elif response.status == 404:
                print(f"Player {player_tag} not found.")
                return None
            else:
                print(f"CoC API returned status {response.status} for player {player_tag}")
                return None
    except Exception as e:
        print(f"Error fetching CoC player data: {e}")
        return None
        
