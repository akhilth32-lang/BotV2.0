# extensions/leaderboard.py
import discord
from discord import app_commands, ui, Interaction, Embed
from discord.ext import commands
from database.player_crud import get_all_players
from config.settings import (
    DEFAULT_COLOR, LEADERBOARD_PAGE_SIZE,
    EMOJI_TROPHY, EMOJI_OFFENSE, EMOJI_DEFENSE,
    IST_OFFSET_HOURS, IST_OFFSET_MINUTES
)
from datetime import datetime, timedelta

class LeaderboardView(ui.View):
    def __init__(self, players, color, title, page=0):
        super().__init__(timeout=None)
        self.players = players
        self.color = color
        self.title = title
        self.page = page

    def get_embed(self):
        start = self.page * LEADERBOARD_PAGE_SIZE
        end = start + LEADERBOARD_PAGE_SIZE
        embed = Embed(title=self.title, color=self.color)

        now_ist = datetime.utcnow() + timedelta(hours=IST_OFFSET_HOURS, minutes=IST_OFFSET_MINUTES)
        embed.set_footer(text=f"Last refreshed: {now_ist.strftime('%d-%m-%Y %I:%M %p')}")

        for i, p in enumerate(self.players[start:end], start=start + 1):
            embed.add_field(
                name=f"{i}. {p['name']} (#{p['player_tag']})",
                value=f"{EMOJI_TROPHY} {p['trophies']} | "
                      f"{EMOJI_OFFENSE} +{p.get('offense_trophies', 0)}/{p.get('offense_attacks', 0)} | "
                      f"{EMOJI_DEFENSE} -{p.get('defense_trophies', 0)}/{p.get('defense_defenses', 0)}\n\u200b",
                inline=False
            )
        return embed

    async def update_message(self, interaction: Interaction):
        await interaction.response.defer()
        self.players = get_all_players()
        await interaction.edit_original_response(embed=self.get_embed(), view=self)

    @ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: Interaction, button: ui.Button):
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)

    @ui.button(label="➡️ Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: Interaction, button: ui.Button):
        if (self.page + 1) * LEADERBOARD_PAGE_SIZE < len(self.players):
            self.page += 1
            await self.update_message(interaction)

    @ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: Interaction, button: ui.Button):
        await self.update_message(interaction)


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Shows the leaderboard")
    @app_commands.describe(
        color="Embed color in hex (default black), e.g. 0x000000",
        name="Leaderboard title"
    )
    async def leaderboard(self, interaction: Interaction, color: str = "0x000000", name: str = "🏆 Leaderboard"):
        await interaction.response.defer()
        try:
            color_value = int(color, 16)
        except Exception:
            color_value = DEFAULT_COLOR

        players = get_all_players()

        view = LeaderboardView(players, color_value, name)
        await interaction.followup.send(embed=view.get_embed(), view=view)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
