# apis/coc_api.py

import aiohttp
import asyncio
from config.settings import COC_API_TOKEN

BASE_URL = "https://api.clashofclans.com/v1"

HEADERS = {
    "Authorization": f"Bearer {COC_API_TOKEN}",
    "Accept": "application/json"
}

class ClashOfClansAPI:

    def __init__(self):
        self.session = aiohttp.ClientSession(headers=HEADERS)

    async def close(self):
        await self.session.close()

    async def get_player(self, player_tag: str):
        """Get player info by tag."""
        player_tag = player_tag.strip('#').upper()
        url = f"{BASE_URL}/players/%23{player_tag}"
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                data = await resp.text()
                raise Exception(f"Failed to get player {player_tag}: {resp.status} - {data}")

    async def verify_player_api_token(self, player_tag: str, token: str):
        """Verify player API Token - using official endpoint if available."""
        # Example endpoint, adjust if required:
        url = f"{BASE_URL}/players/%23{player_tag}/verifytoken"
        # For verification, token is passed differently possibly, here simulating with header
        headers = HEADERS.copy()
        headers['Authorization'] = f"Bearer {token}"
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                return resp.status == 200

    async def get_location_leaderboard(self, location_id: str, limit=30, after=None):
        """Get leaderboard for a given location id."""
        url = f"{BASE_URL}/locations/{location_id}/rankings/players?limit={limit}"
        if after:
            url += f"&after={after}"
        async with self.session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                data = await resp.text()
                raise Exception(f"Failed to get leaderboard for {location_id}: {resp.status} - {data}")
            
