# extensions/current_leaderboard.py

import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans
from config import emoji
from datetime import datetime, timezone

LEADERBOARD_PAGE_SIZE = 30

# Example Legend League Seasons - adjust to your actual schedule
LEGEND_SEASONS_2025 = [
    {"start": datetime(2025, 7, 1, tzinfo=timezone.utc), "end": datetime(2025, 7, 29, tzinfo=timezone.utc), "duration_days": 28},
]

def get_current_season_day():
    now = datetime.now(timezone.utc)
    for season in LEGEND_SEASONS_2025:
        if season["start"] <= now < season["end"]:
            elapsed = (now - season["start"]).days + 1
            total = season["duration_days"]
            season_month = season["start"].strftime("%Y-%m")
            now_local = now.astimezone()
            return elapsed, total, season_month, now_local
    return None, None, None, datetime.now().astimezone()

class LeaderboardView(discord.ui.View):
    def __init__(self, bot, players, leaderboard_name):
        super().__init__(timeout=600)
        self.bot = bot
        self.players = players
        self.page = 1
        self.leaderboard_name = leaderboard_name
        self.max_pages = (len(players) + LEADERBOARD_PAGE_SIZE - 1) // LEADERBOARD_PAGE_SIZE

    def build_embed(self):
        start = (self.page - 1) * LEADERBOARD_PAGE_SIZE
        end = start + LEADERBOARD_PAGE_SIZE
        page_players = self.players[start:end]

        description_lines = []
        for idx, player in enumerate(page_players, start=start + 1):
            name = to_bold_gg_sans(player.get("name", "Unknown"))
            tag = player.get("tag", "")
            trophies = player.get("trophies", 0)
            offense = f"{emoji.EMOJIS['offense']} +0/0"
            defense = f"{emoji.EMOJIS['defense']} -0/0"
            description_lines.append(f"{idx}. {name} 🏆 {trophies} {offense} {defense} ({tag})")
            description_lines.append("")  # Add small blank line space

        embed = create_embed(
            title=f"{self.leaderboard_name} Legend League Leaderboard (Page {self.page}/{self.max_pages})",
            description="\n".join(description_lines),
            color=discord.Color.dark_gray()
        )

        elapsed, total, season_month, now_local = get_current_season_day()
        if elapsed and total and season_month:
            footer_text = f"Day {elapsed}/{total} ({season_month}) | Today at {now_local.strftime('%I:%M %p')}"
        else:
            footer_text = f"Date unknown | {now_local.strftime('%m/%d/%Y %I:%M %p')}"
        embed.set_footer(text=footer_text)

        return embed

    async def update_message(self, interaction):
        embed = self.build_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, interaction, button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are on the first page.", ephemeral=True)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh(self, interaction, button):
        await interaction.response.defer()
        # Optionally: refresh players from DB here if dynamic data needed
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction, button):
        if self.page < self.max_pages:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are on the last page.", ephemeral=True)

class CurrentLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="current_leaderboard", description="Show current Legend League leaderboard")
    @app_commands.describe(leaderboard_name="Leaderboard location or region name")
    async def current_leaderboard(self, interaction: discord.Interaction, leaderboard_name: str = "Global"):
        await interaction.response.defer()

        # Example method to fetch players, replace with your real API/db call
        players = await self.fetch_leaderboard_players(leaderboard_name)

        if not players:
            await interaction.followup.send("No leaderboard data found for this region.")
            return

        view = LeaderboardView(self.bot, players, leaderboard_name)
        embed = view.build_embed()
        await interaction.followup.send(embed=embed, view=view)

    async def fetch_leaderboard_players(self, location: str):
        # Dummy example list, replace this with your actual fetching logic
        # Fetched players should be list of dicts with keys:
        #   name, tag, trophies, offense, defense, etc.
        dummy_players = [
            {"name": "Player1", "tag": "#ABC123", "trophies": 3500},
            {"name": "Player2", "tag": "#DEF456", "trophies": 3400},
            # ... more players ...
        ]
        return dummy_players  # Replace with API call or DB query filtered by location

async def setup(bot):
    await bot.add_cog(CurrentLeaderboard(bot))
                      
