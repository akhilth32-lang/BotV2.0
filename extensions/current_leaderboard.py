# extensions/current_leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands, tasks
from apis.leaderboard_fetcher import LeaderboardFetcher
from config import emoji
from config.legend_season import LEGEND_SEASONS_2025
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans
from datetime import datetime, timezone

PAGE_SIZE = 30

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
        self.message = None
    
    async def update_message(self, interaction=None):
        try:
            data = await self.fetcher.fetch_leaderboard_page(self.location_id, self.page)
        except Exception as e:
            if interaction:
                await interaction.response.send_message(f"Error fetching leaderboard: {str(e)}", ephemeral=True)
            return

        if not data:
            if interaction:
                await interaction.response.send_message("No leaderboard data found.", ephemeral=True)
            return

        description_lines = []
        start_rank = (self.page - 1) * PAGE_SIZE + 1
        for idx, player in enumerate(data, start=start_rank):
            name = to_bold_gg_sans(player.get("name", "Unknown"))
            tag = player.get("tag", "")
            trophies = player.get("trophies", 0)
            offense = f"{emoji.EMOJIS['offense']} +0/0"
            defense = f"{emoji.EMOJIS['defense']} -0/0"
            line = f"{idx}. {name} 🏆{trophies} {offense} {defense} ({tag})"
            description_lines.append(line)

        embed = create_embed(
            title="Global Legend League Current Leaderboard",
            description="\n".join(description_lines),
            color=discord.Color.dark_theme()
        )

        elapsed, total, season_month, now = get_current_season_day()
        if elapsed and total and season_month:
            now_local = now.astimezone()
            today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if now_local > today_midnight:
                footer_str = f"Day {elapsed}/{total} ({season_month}) | Today at {now_local.strftime('%I:%M %p')}"
            else:
                footer_str = f"Day {elapsed}/{total} ({season_month}) | {now_local.strftime('%m/%d/%Y %I:%M %p')}"
        else:
            footer_str = f"Date unknown | {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
        
        embed.set_footer(text=footer_str)

        if interaction:
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            self.message = await self.bot.get_channel(self.channel_id).send(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the first page.", ephemeral=True)
    
    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.gray)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Assuming max 7 pages (200 players / 30 per page approx)
        if self.page < 7:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the last page.", ephemeral=True)

class CurrentLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="current_leaderboard", description="Shows the current Global Legend League leaderboard (top 200)")
    async def current_leaderboard(self, interaction: discord.Interaction):
        view = LeaderboardView(self.bot)
        await interaction.response.defer()
        await view.update_message(interaction)
        await interaction.followup.send("Leaderboard loaded with navigation buttons.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CurrentLeaderboard(bot))
        
    
