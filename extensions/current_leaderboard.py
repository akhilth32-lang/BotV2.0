# extensions/current_leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from apis.leaderboard_fetcher import LeaderboardFetcher
from config.legend_season import LEGEND_SEASONS_2025
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans
from datetime import datetime, timezone
from config.countries import COUNTRIES

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


def format_player_line(rank: int, player: dict) -> str:
    """Return formatted leaderboard line for a player"""
    name = to_bold_gg_sans(player.get("name", "Unknown"))
    clan = player.get("clan", {}).get("name", "")
    trophies = player.get("trophies", 0)

    # Highlight top 3 ranks
    if rank == 1:
        prefix = "🥇"
    elif rank == 2:
        prefix = "🥈"
    elif rank == 3:
        prefix = "🥉"
    else:
        prefix = "🏆"

    line = f"{prefix} {trophies} | {name}"
    if clan:
        line += f"\n   *{clan}*"
    return line


class CountrySelect(discord.ui.Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label=c["name"], value=str(c["id"]))
            for c in COUNTRIES
        ]
        super().__init__(
            placeholder="Select a country/region...",
            options=options,
            min_values=1,
            max_values=1
        )
        self.parent_view = view

    async def callback(self, interaction: discord.Interaction):
        self.parent_view.location_id = self.values[0]
        self.parent_view.players_cache = []  # clear cache for new country
        self.parent_view.page = 1
        await self.parent_view.update_message(interaction)


class LeaderboardView(discord.ui.View):
    def __init__(self, bot, location_id="global"):
        super().__init__(timeout=600)
        self.bot = bot
        self.location_id = location_id
        self.page = 1
        self.fetcher = LeaderboardFetcher()
        self.players_cache = []  # Cache all 200 players

        # Add country selector
        self.add_item(CountrySelect(self))

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

            description_lines = [
                format_player_line(idx, player)
                for idx, player in enumerate(players, start=start_index + 1)
            ]

            country_name = next(
                (c["name"] for c in COUNTRIES if str(c["id"]) == str(self.location_id)),
                "Global"
            )

            embed = create_embed(
                title=f"{country_name} Legend League Current Leaderboard",
                description="\n\n".join(description_lines) if description_lines else "No data found.",
                color=discord.Color.dark_gray()
            )

            # Footer with season info
            elapsed, total, season_month, now = get_current_season_day()
            if elapsed and total and season_month:
                now_local = now.astimezone()
                footer_str = f"Day {elapsed}/{total} ({season_month}) | {now_local.strftime('%I:%M %p')}"
            else:
                footer_str = f"Date unknown | {datetime.now().strftime('%m/%d/%Y %I:%M %p')}"

            total_pages = max(1, (len(self.players_cache) // PAGE_SIZE))
            embed.set_footer(text=f"{footer_str} • Page {self.page}/{total_pages}")
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

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the first page.", ephemeral=True)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.danger)
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

    @app_commands.command(
        name="current_leaderboard",
        description="Shows the current Legend League leaderboard (top 200, 50 per page)"
    )
    async def current_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        view = LeaderboardView(self.bot)
        embed = await view.fetch_and_build_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(CurrentLeaderboard(bot))
