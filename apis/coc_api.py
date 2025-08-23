import coc
import asyncio
from config.settings import COC_API_TOKEN

class CocClient:
    def __init__(self):
        self.client = None

    async def start(self):
        if self.client is None:
            self.client = coc.Client(api_key=COC_API_TOKEN)

    async def get_player(self, player_tag):
        if self.client is None:
            await self.start()
        return await self.client.get_player(player_tag)

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None
            
