# apis/leaderboard_fetcher.py

from typing import Optional
from apis.coc_api import ClashOfClansAPI
from config.settings import CURRENT_LEADERBOARD_PAGE_SIZE

class LeaderboardFetcher:
    def __init__(self):
        self.api = ClashOfClansAPI()
        self.page_afters = {1: None}  # Store last player's tag for each page for 'after' param

    async def fetch_leaderboard_page(self, location_id: str, page: int = 1):
        """Fetch a page of leaderboard players from the official API."""
        limit = CURRENT_LEADERBOARD_PAGE_SIZE
        after = self.page_afters.get(page, None)

        result = await self.api.get_location_leaderboard(location_id, limit=limit, after=after)
        items = result.get("items", [])

        # Cache the last player's tag of this page to use as 'after' for next page
        if items:
            last_tag = items[-1]["tag"]
            self.page_afters[page + 1] = last_tag

        return items

    async def close(self):
        await self.api.close()
        
