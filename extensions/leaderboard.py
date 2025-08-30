# extensions/leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud, leaderboard_snapshot_crud
from config import legend_season
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans
from utils.time_helpers import get_current_legend_season_and_day
import datetime

LEADERBOARD_PAGE_SIZE = 20

class LeaderboardView(discord.ui.View):
    def __init__(self, bot, leaderboard_name, color, day, season_number, total_days):
        super().__init__(timeout=None)
        self.bot = bot
        self.leaderboard_name = leaderboard_name
        self.color = color
        self.day = day
        self.current_page = 0
        self.season_number = season_number
        self.total_days = total_days
        self.players = []

    async def load_players(self):
        current_season, current_day = get_current_legend_season_and_day(legend_season.LEGEND_SEASONS_2025)
        target_day = self.day if self.day > 0 else current_day

        if self.day == 0 or self.day == current_day:
            self.players = await player_crud.get_all_linked_players()
        else:
            snapshot = await leaderboard_snapshot_crud.get_snapshot(self.season_number, target_day)
            if snapshot and "leaderboard_data" in snapshot:
                self.players = snapshot["leaderboard_data"]
            else:
                self.players = []
        self.players.sort(key=lambda p: p.get("trophies", 0), reverse=True)

    def create_embed(self):
        start = self.current_page * LEADERBOARD_PAGE_SIZE
        end = start + LEADERBOARD_PAGE_SIZE
        page_players = self.players[start:end]

        description_lines = []
        for idx, player in enumerate(page_players, start=start + 1):
            name = to_bold_gg_sans(player.get("player_name", "Unknown"))
            tag = player.get("player_tag", "N/A")
            trophies = player.get("trophies", 0)
            offense_change = player.get("offense_trophies", 0)

            current_offense_attacks = player.get("offense_attacks", 0)
            # Display total daily offense attacks directly to avoid zero display issue
            offense_attack_diff = current_offense_attacks

            defense_change = player.get("defense_trophies", 0)
            defense_defends = player.get("defense_defenses", 0)

            trophy_emoji = EMOJIS.get("trophy", "🏆")
            offense_emoji = EMOJIS.get("offense", "⚔️")
            defense_emoji = EMOJIS.get("defense", "🛡️")

            line1 = f"{idx}. {name} ({tag})"
            line2 = (
                f"{trophy_emoji} {trophies} | "
                f"{offense_emoji} `{offense_change:+}/{offense_attack_diff}` | "
                f"{defense_emoji} `-{abs(defense_change)}/{defense_defends}`"
            )

            description_lines.append(f"{line1}\n{line2}\n")

        leaderboard_emoji = EMOJIS.get("leaderboard", "")
        embed = create_embed(
            title=f"{leaderboard_emoji} {self.leaderboard_name} Leaderboard",
            description="\n".join(description_lines),
            color=discord.Color(int(self.color.replace('#', ''), 16))
        )

        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_local = now_utc.astimezone()
        today_midnight = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        month_year = next(
            (s["start"].strftime("%Y-%m") for s in legend_season.LEGEND_SEASONS_2025 if s["season_number"] == self.season_number),
            ""
        )
        day_display = self.day if self.day > 0 else get_current_legend_season_and_day(legend_season.LEGEND_SEASONS_2025)[1]
        if day_display and self.total_days and month_year:
            if now_local > today_midnight:
                footer_text = f"Day {day_display}/{self.total_days} ({month_year}) | Today at {now_local.strftime('%I:%M %p')}"
            else:
                footer_text = f"Day {day_display}/{self.total_days} ({month_year}) | {now_local.strftime('%m/%d/%Y %I:%M %p')}"
        else:
            footer_text = f"Date unknown | {now_local.strftime('%m/%d/%Y %I:%M %p')}"

        embed.set_footer(text=footer_text)
        return embed

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("Already at the first page.", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        max_page = (len(self.players) - 1) // LEADERBOARD_PAGE_SIZE
        if self.current_page < max_page:
            self.current_page += 1
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("Already at the last page.", ephemeral=True)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.load_players()
        self.current_page = 0
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="leaderboard",
        description="Show leaderboard of all linked Clash of Clans player accounts with navigation buttons"
    )
    @app_commands.describe(
        leaderboard_name="Name of the leaderboard to show",
        color="Embed color in hex (e.g. #000000 for black, default black)",
        day="Legend league day snapshot to view (default current day)"
    )
    async def leaderboard(self, interaction: discord.Interaction, leaderboard_name: str, color: str = "#000000", day: int = 0):
        await interaction.response.defer()

        season_number, current_day = get_current_legend_season_and_day(legend_season.LEGEND_SEASONS_2025)
        total_days = next(
            (season["duration_days"] for season in legend_season.LEGEND_SEASONS_2025 if season["season_number"] == season_number),
            None
        )

        view = LeaderboardView(self.bot, leaderboard_name, color, day, season_number, total_days)
        await view.load_players()

        if not view.players:
            await interaction.followup.send(f"No data found for season {season_number} day {day}.")
            return
            
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
        
