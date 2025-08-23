# extensions/current_leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from apis.leaderboard_fetcher import LeaderboardFetcher
from config import countries, emoji, fonts
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans, to_regular_gg_sans

PAGE_SIZE = 30

class CurrentLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.fetcher = LeaderboardFetcher()

    @app_commands.command(name="current_leaderboard", description="Shows the current Global Legend League leaderboard (top 200)")
    @app_commands.describe(page="Leaderboard page number (default 1)")
    async def current_leaderboard(self, interaction: discord.Interaction, page: int = 1):
        await interaction.response.defer()

        location_id = "global"
        try:
            data = await self.fetcher.fetch_leaderboard_page(location_id, page)
        except Exception as e:
            await interaction.followup.send(f"Error fetching leaderboard: {str(e)}", ephemeral=True)
            return

        if not data:
            await interaction.followup.send("No leaderboard data found.", ephemeral=True)
            return

        description_lines = []
        start_rank = (page - 1) * PAGE_SIZE + 1
        for idx, player in enumerate(data, start=start_rank):
            name = to_bold_gg_sans(player.get("name", "Unknown"))
            tag = player.get("tag", "")
            trophies = player.get("trophies", 0)
            # Using live stats for offence and defence not available from API here, placeholders
            offense = f"{emoji.EMOJIS['offense']} +0/0"
            defense = f"{emoji.EMOJIS['defense']} -0/0"
            line = f"{idx}. {name} 🏆{trophies} {offense} {defense} ({tag})"
            description_lines.append(line)

        embed = create_embed(
            title="Global Legend League Current Leaderboard",
            description="\n".join(description_lines),
            color=discord.Color.dark_theme()
        )
        embed.set_footer(text=f"Page {page} — Use buttons to navigate, refresh data")

        # Send embed with buttons (refresh, previous, next)
        # You will implement your button logic in the commands
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CurrentLeaderboard(bot))
    
