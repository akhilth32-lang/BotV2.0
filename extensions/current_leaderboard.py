# extensions/leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud, leaderboard_snapshot_crud
from config import legend_season
from config.emoji import EMOJIS
from config.fonts import to_bold_gg
from utils.embed_helpers import create_embed
from utils.time_helpers import get_current_legend_season_and_day
import datetime

LEADERBOARD_PAGE_SIZE = 50  # show 50 players per page


class LeaderboardView(discord.ui.View):
    def __init__(self, bot, players, country, page=0):
        super().__init__(timeout=60)
        self.bot = bot
        self.players = players
        self.page = page
        self.country = country

        self.add_item(discord.ui.Button(label="Previous", style=discord.ButtonStyle.secondary, custom_id="prev"))
        self.add_item(discord.ui.Button(label="Refresh", style=discord.ButtonStyle.secondary, custom_id="refresh"))
        self.add_item(discord.ui.Button(label="Next", style=discord.ButtonStyle.secondary, custom_id="next"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        embed = await create_leaderboard_embed(self.players, self.page, self.country)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        # fetch latest players again
        players = await player_crud.get_all_players_sorted(self.country)
        self.players = players
        embed = await create_leaderboard_embed(players, self.page, self.country)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if (self.page + 1) * LEADERBOARD_PAGE_SIZE < len(self.players):
            self.page += 1
        embed = await create_leaderboard_embed(self.players, self.page, self.country)
        await interaction.response.edit_message(embed=embed, view=self)


async def create_leaderboard_embed(players, page, country):
    start = page * LEADERBOARD_PAGE_SIZE
    end = start + LEADERBOARD_PAGE_SIZE
    page_players = players[start:end]

    desc = []
    for i, player in enumerate(page_players, start=start + 1):
        line = f"{i}. {EMOJIS['trophy']} {player['trophies']} | {to_bold_gg(player['name'])}"
        desc.append(line)

    if not desc:
        desc = ["No players found for this country."]

    embed = discord.Embed(
        title=f"🏆 {country.upper()} Leaderboard",
        description="\n".join(desc),
        color=discord.Color.dark_gray()
    )

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    embed.set_footer(text=f"Page {page+1} | Last updated {now}")

    return embed


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show the Legend League leaderboard")
    @app_commands.describe(country="Country code (check countries.py)")
    async def leaderboard(self, interaction: discord.Interaction, country: str):
        players = await player_crud.get_all_players_sorted(country)
        embed = await create_leaderboard_embed(players, 0, country)
        view = LeaderboardView(self.bot, players, country, page=0)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
