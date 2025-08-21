# extensions/current_leaderboard.py

import discord
from discord import app_commands, ui, Interaction, Embed
from discord.ext import commands
import aiohttp
from datetime import datetime
from config.settings import COC_API_TOKEN
from typing import List

PAGE_SIZE = 25

class CurrentLeaderboardView(ui.View):
    def __init__(self, players: List[dict], page=0):
        super().__init__(timeout=None)
        self.players = players
        self.page = page

    def get_embed(self) -> Embed:
        embed = Embed(title="🔥 Current Legend League Leaderboard (Top 200)", color=0x118EF5)
        start = self.page * PAGE_SIZE
        end = start + PAGE_SIZE
        for idx, player in enumerate(self.players[start:end], start=start + 1):
            embed.add_field(
                name=f"{idx}. {player['name']} (#{player['tag']})",
                value=f"🏆 Trophies: {player['trophies']} | Town Hall: {player.get('townhall', 'N/A')}",
                inline=False,
            )
        embed.set_footer(text=f"Showing players {start + 1} to {min(end, len(self.players))} of {len(self.players)}")
        return embed

    @ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: Interaction, button: ui.Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @ui.button(label="➡️ Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: Interaction, button: ui.Button):
        if (self.page + 1) * PAGE_SIZE < len(self.players):
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)


class CurrentLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def fetch_current_leaderboard(self):
        url = "https://api.clashofclans.com/v1/locations/global/rankings/players"
        headers = {
            "Authorization": f"Bearer {COC_API_TOKEN}",
            "Accept": "application/json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return data.get("items", [])[:200]

    @app_commands.command(name="leaderboardcurrent", description="Shows current official Clash of Clans Legend League leaderboard")
    async def leaderboard_current(self, interaction: Interaction):
        await interaction.response.defer()
        players = await self.fetch_current_leaderboard()
        if not players:
            await interaction.followup.send("Failed to fetch leaderboard data.", ephemeral=True)
            return

        view = CurrentLeaderboardView(players)
        await interaction.followup.send(embed=view.get_embed(), view=view)

async def setup(bot):
    await bot.add_cog(CurrentLeaderboard(bot))
        
