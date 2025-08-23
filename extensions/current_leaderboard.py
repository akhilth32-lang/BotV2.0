# extensions/current_leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from apis.leaderboard_fetcher import LeaderboardFetcher
from config import emoji
from config.legend_season import LEGEND_SEASONS_2025
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans
from datetime import datetime, timezone

PAGE_SIZE = 50  # Number of players per page

def get_current_season_day():
    now = datetime.now(timezone.utc)
    for season in LEGEND_SEASONS_2025:
        if season["start"] <= now < season["end"]:
            elapsed = (now - season["start"]).days + 1
            total = season["duration_days"]
            season_month = season["start"].strftime("%Y-%m")
            return elapsed, total, season_month, now
    return None, None, None, now

class LeaderboardView(discord.ui.View):
    def __init__(self, bot, location_id="global"):
        super().__init__(timeout=600)
        self.bot = bot
        self.location_id = location_id
        self.page = 1
        self.fetcher = LeaderboardFetcher()
        self.cached_players = []  # Cache full leaderboard players for pagination

    async def fetch_and_cache_leaderboard(self):
        """Fetch full leaderboard bulk once and cache it."""
        self.cached_players = await self.fetcher.fetch_full_leaderboard(self.location_id)

    def build_embed(self, page):
        """Paginate from cached_players locally for fast response."""
        start = (page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        players = self.cached_players[start:end]

        description_lines = []
        for idx, player in enumerate(players, start=start + 1):
            name = to_bold_gg_sans(player.get("name", "Unknown"))
            tag = player.get("tag", "")
            trophies = player.get("trophies", 0)
            offense = f"{emoji.EMOJIS['offense']} +0/0"
            defense = f"{emoji.EMOJIS['defense']} -0/0"
            description_lines.append(f"{idx}. {name} 🏆 {trophies} {offense} {defense} ({tag})")

        embed = create_embed(
            title=f"Global Legend League Current Leaderboard — Page {page}",
            description="\n".join(description_lines) if description_lines else "No data found.",
            color=discord.Color.dark_gray()
        )

        elapsed, total, season_month, now = get_current_season_day()
        now_local = now.astimezone()
        today_midnight = now_local.replace(hour=0, minute=0, second=0, microsecond=0)

        if elapsed and total and season_month:
            if now_local > today_midnight:
                footer_str = f"Day {elapsed}/{total} ({season_month}) | Today at {now_local.strftime('%I:%M %p')}"
            else:
                footer_str = f"Day {elapsed}/{total} ({season_month}) | {now_local.strftime('%m/%d/%Y %I:%M %p')}"
        else:
            footer_str = f"Date unknown | {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"

        embed.set_footer(text=footer_str)
        return embed

    async def update_message(self, interaction):
        embed = self.build_embed(self.page)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction, button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the first page.", ephemeral=True)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_button(self, interaction, button):
        await interaction.response.defer()
        await self.fetch_and_cache_leaderboard()  # Refresh cached data
        self.page = 1
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction, button):
        max_pages = (len(self.cached_players) - 1) // PAGE_SIZE + 1
        if self.page < max_pages:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the last page.", ephemeral=True)

class CurrentLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="current_leaderboard", description="Shows the current Global Legend League leaderboard (top 200)")
    async def current_leaderboard(self, interaction):
        await interaction.response.defer(thinking=True)
        view = LeaderboardView(self.bot)
        await view.fetch_and_cache_leaderboard()
        embed = view.build_embed(view.page)
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(CurrentLeaderboard(bot))
        
