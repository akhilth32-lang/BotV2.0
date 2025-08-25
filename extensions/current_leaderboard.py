# extensions/current_leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from apis.leaderboard_fetcher import LeaderboardFetcher
from config import emoji
from config.legend_season import LEGEND_SEASONS_2025
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans, to_regular_gg_sans
from config.countries import COUNTRIES
from datetime import datetime, timezone

PAGE_SIZE = 50  # Show 50 players per page
MAX_PLAYERS = 200  # Limit to top 200


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
    def __init__(self, bot, location_id="global", country_name="Global", country_code="global"):
        super().__init__(timeout=600)
        self.bot = bot
        self.location_id = location_id
        self.country_name = country_name
        self.country_code = country_code
        self.page = 1
        self.fetcher = LeaderboardFetcher()
        self.players_cache = []  # Cache all 200 players

    async def fetch_all_players(self):
        """Fetch top 200 players from API once and store in cache."""
        if not self.players_cache:
            try:
                result = await self.fetcher.api.get_location_leaderboard(
                    self.location_id, limit=MAX_PLAYERS
                )
                self.players_cache = result.get("items", [])
            except Exception as e:
                raise RuntimeError(f"Failed to fetch leaderboard: {str(e)}")

    async def fetch_and_build_embed(self):
        try:
            await self.fetch_all_players()

            # Pagination
            start_index = (self.page - 1) * PAGE_SIZE
            end_index = start_index + PAGE_SIZE
            players = self.players_cache[start_index:end_index]

            description_lines = []
            trophy_emoji = emoji.EMOJIS.get("trophy", "🏆")
            for idx, player in enumerate(players, start=start_index + 1):
                rank_str = to_bold_gg_sans(f"#{idx:<3}")  # Rank bold
                trophies = to_regular_gg_sans(str(player.get("trophies", 0)))
                name = to_regular_gg_sans(player.get("name", "Unknown"))
                # ✅ Format: Bold rank, rest regular
                line = f"{rank_str} {trophy_emoji} {trophies} | {name}"
                description_lines.append(line)

            # Country emoji from emoji.COUNTRY_EMOJIS
            country_emoji = emoji.COUNTRY_EMOJIS.get(self.country_code, "🌍")
            embed = create_embed(
                title=f"{country_emoji} {self.country_name} Legend League Leaderboard",
                description="\n".join(description_lines) if description_lines else "No data found.",
                color=discord.Color.dark_gray()
            )

            # Footer with season info (no page number)
            elapsed, total, season_month, now = get_current_season_day()
            if elapsed and total and season_month:
                now_local = now.astimezone()
                today_midnight = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
                if now_local > today_midnight:
                    footer_str = f"Day {elapsed}/{total} ({season_month}) | Today at {now_local.strftime('%I:%M %p')}"
                else:
                    footer_str = f"Day {elapsed}/{total} ({season_month}) | {now_local.strftime('%m/%d/%Y %I:%M %p')}"
            else:
                footer_str = f"Date unknown | {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"

            embed.set_footer(text=footer_str)
            return embed

        except Exception as e:
            return create_embed(
                title="Error",
                description=f"⚠️ Failed to fetch leaderboard: `{str(e)}`",
                color=discord.Color.red()
            )

    async def update_message(self, interaction):
        embed = await self.fetch_and_build_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    # ✅ All buttons now black (secondary)
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the first page.", ephemeral=True)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.players_cache = []  # Clear cache to re-fetch
        self.page = 1
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        max_pages = (MAX_PLAYERS // PAGE_SIZE)
        if self.page < max_pages:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the last page.", ephemeral=True)


class CurrentLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Build choices dynamically from COUNTRIES
    country_choices = [
        app_commands.Choice(name=c["name"], value=str(c["id"]))
        for c in COUNTRIES
    ]

    @app_commands.command(
        name="current_leaderboard",
        description="Shows the current Legend League leaderboard (top 200, 50 per page)"
    )
    @app_commands.describe(country="Select a country/local leaderboard")
    @app_commands.choices(country=country_choices)
    async def current_leaderboard(self, interaction: discord.Interaction, country: app_commands.Choice[str] = None):
        await interaction.response.defer(thinking=True)

        # If no country given, default to global
        selected_country_id = "global"
        selected_country_name = "Global"
        selected_country_code = "global"

        if country:
            selected_country_id = country.value
            match = next((c for c in COUNTRIES if str(c["id"]) == country.value), None)
            if match:
                selected_country_name = match["name"]
                selected_country_code = match.get("countryCode", "global")

        view = LeaderboardView(
            self.bot,
            location_id=selected_country_id,
            country_name=selected_country_name,
            country_code=selected_country_code
        )
        embed = await view.fetch_and_build_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(CurrentLeaderboard(bot))
