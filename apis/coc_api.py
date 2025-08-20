# apis/coc_api.py
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

COC_API_TOKEN = os.getenv("COC_API_TOKEN")
COC_API_BASE_URL = "https://api.clashofclans.com/v1"

HEADERS = {
    "Authorization": f"Bearer {COC_API_TOKEN}",
    "Accept": "application/json"
}


async def fetch_player_data(session, player_tag: str):
    tag = player_tag if player_tag.startswith("#") else f"#{player_tag}"
    tag_encoded = tag.replace("#", "%23")
    url = f"{COC_API_BASE_URL}/players/{tag_encoded}"
    async with session.get(url, headers=HEADERS) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            print(f"COC API error: {resp.status} for tag {player_tag}")
            return None


async def fetch_legend_leaderboard(session):
    url = f"{COC_API_BASE_URL}/leaderboards/players/legend"
    async with session.get(url, headers=HEADERS) as resp:
        if resp.status == 200:
            return await resp.json()
        else:
            print(f"COC API error: {resp.status} for legend leaderboard")
            return None
          
