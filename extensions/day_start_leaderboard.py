# extensions/day_start_leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database.leaderboard_snapshot_crud import get_snapshot
from config import emoji
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans, to_regular_gg_sans
from config.legend_season import LEGEND_SEASONS_2025
from utils.time_helpers import get_current_legend_season_and_day
from config.countries import COUNTRIES
from datetime import datetime, timezone

PAGE_SIZE = 50  # same as current leaderboard


class DayStartLeaderboardView(discord.ui.View):
    def __init__(self, snapshot_data, season, day, country_name, country_code):
        super().__init__(timeout=600)
        self.snapshot_data = snapshot_data
        self.season = season
        self.day = day
        self.country_name = country_name
        self.country_code = country_code
        self.page = 1

    async def build_embed(self):
        start_index = (self.page - 1) * PAGE_SIZE
        end_index = start_index + PAGE_SIZE
        players = self.snapshot_data[start_index:end_index]

        description_lines = []
        trophy_emoji = emoji.EMOJIS.get("trophy", "🏆")
        for idx, player in enumerate(players, start=start_index + 1):
            rank_str = to_bold_gg_sans(f"#{idx:<3}")
            trophies = to_regular_gg_sans(str(player.get("trophies", 0)))
            name = to_regular_gg_sans(player.get("player_name", "Unknown"))
            line = f"{rank_str} {trophy_emoji} {trophies} | {name}"
            description_lines.append(line)

        # Country emoji
        country_emoji = emoji.COUNTRY_EMOJIS.get(self.country_code, "🌍")

        embed = create_embed(
            title=f"{country_emoji} {self.country_name} Legend League Snapshot (Day {self.day}, Season {self.season})",
            description="\n".join(description_lines) if description_lines else "No data found.",
            color=discord.Color(0x2c2f33)
        )

        now = datetime.now(timezone.utc).astimezone()
        footer_str = f"Day {self.day} (Season {self.season}) | Snapshot at {now.strftime('%I:%M %p')} | Page {self.page}"
        embed.set_footer(text=footer_str)
        return embed

    async def update_message(self, interaction: discord.Interaction):
        embed = await self.build_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the first page.", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        max_pages = (len(self.snapshot_data) + PAGE_SIZE - 1) // PAGE_SIZE
        if self.page < max_pages:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the last page.", ephemeral=True)


class DayStartLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Build choices dynamically from COUNTRIES
    country_choices = [
        app_commands.Choice(name=c["name"], value=str(c["id"]))
        for c in COUNTRIES
    ]

    @app_commands.command(
        name="day_start_leaderboard",
        description="Shows the Legend League snapshot leaderboard at 10:30 AM IST reset"
    )
    @app_commands.describe(
        page="Leaderboard page number (default 1)",
        country="Select a country/local leaderboard"
    )
    @app_commands.choices(country=country_choices)
    async def day_start_leaderboard(
        self,
        interaction: discord.Interaction,
        page: int = 1,
        country: app_commands.Choice[str] = None
    ):
        await interaction.response.defer(thinking=True)

        # Current season/day
        season, day = get_current_legend_season_and_day(LEGEND_SEASONS_2025)

        # Default global snapshot
        selected_country_name = "Global"
        selected_country_code = "global"
        country_code_for_query = "global"

        if country:
            match = next((c for c in COUNTRIES if str(c["id"]) == country.value), None)
            if match:
                selected_country_name = match["name"]
                selected_country_code = match.get("countryCode", "global")
                country_code_for_query = selected_country_code

        snapshot = await get_snapshot(season, day, country_code_for_query)
        if not snapshot:
            await interaction.followup.send(
                f"⚠️ No snapshot found for {selected_country_name} leaderboard (Day {day}, Season {season}).",
                ephemeral=True
            )
            return

        leaderboard_data = snapshot.get("leaderboard_data", [])

        # View with pagination
        view = DayStartLeaderboardView(
            leaderboard_data, season, day, selected_country_name, selected_country_code
        )
        view.page = page

        embed = await view.build_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(DayStartLeaderboard(bot))
