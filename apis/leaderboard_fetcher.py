# apis/leaderboard_fetcher.py

from typing import Optional
from apis.coc_api import ClashOfClansAPI
from config.settings import CURRENT_LEADERBOARD_PAGE_SIZE

class LeaderboardFetcher:
    def __init__(self):
        self.api = ClashOfClansAPI()

    async def fetch_leaderboard_page(self, location_id: str, page: int = 1):
        """Fetch a page of leaderboard players from the official API."""
        # The API uses 'after' with tag of last player for pagination, translate page to after accordingly
        # Here we simplify by fetching pages sequentially, or by using 'after' param stored externally
        
        limit = CURRENT_LEADERBOARD_PAGE_SIZE
        after = None

        # For high efficiency, maintain cache/maps for tag 'after' positions if needed

        result = await self.api.get_location_leaderboard(location_id, limit=limit, after=after)
        return result.get("items", [])

    async def close(self):
        await self.api.close()
