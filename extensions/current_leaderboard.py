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
        self.page_afters = {1: None}  # Tracks the 'after' tag for pagination

    async def fetch_and_build_embed(self):
        after = self.page_afters.get(self.page)
        try:
            # Fetch leaderboard page
            result = await self.fetcher.api.get_location_leaderboard(
                self.location_id, limit=PAGE_SIZE, after=after
            )
            players = result.get("items", [])

            # Handle empty page fallback
            if not players and self.page != 1:
                self.page = max(1, self.page - 1)
                after = self.page_afters.get(self.page)
                result = await self.fetcher.api.get_location_leaderboard(
                    self.location_id, limit=PAGE_SIZE, after=after
                )
                players = result.get("items", [])

            # Cache 'after' marker for the next or reset if invalid
            if players:
                self.page_afters[self.page + 1] = players[-1]["tag"]

            description_lines = []
            start_rank = (self.page - 1) * PAGE_SIZE + 1
            for idx, player in enumerate(players, start=start_rank):
                name = to_bold_gg_sans(player.get("name", "Unknown"))
                tag = player.get("tag", "")
                trophies = player.get("trophies", 0)
                offense = f"{emoji.EMOJIS['offense']} +0/0"
                defense = f"{emoji.EMOJIS['defense']} -0/0"
                line = f"{idx}. {name} 🏆 {trophies} {offense} {defense} ({tag})"
                description_lines.append(line)

            embed = create_embed(
                title="Global Legend League Current Leaderboard",
                description="\n".join(description_lines) if description_lines else "No data found.",
                color=discord.Color.dark_gray()
            )

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
            err_str = str(e)
            if "Invalid 'after' or 'before' marker" in err_str:
                # Reset pagination state on invalid marker error
                keys_to_remove = [k for k in self.page_afters if k >= self.page]
                for k in keys_to_remove:
                    self.page_afters.pop(k, None)
                self.page_afters[1] = None
                self.page = 1
                # Recursive retry with reset state
                return await self.fetch_and_build_embed()
            else:
                return create_embed(
                    title="Error",
                    description=f"⚠️ Failed to fetch leaderboard: `{err_str}`",
                    color=discord.Color.red()
                )

    async def update_message(self, interaction):
        embed = await self.fetch_and_build_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the first page.", ephemeral=True)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.secondary)
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Reset to first page and clear pagination tokens
        self.page = 1
        self.page_afters = {1: None}
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Cannot know max page, but if next page fetch fails, it will reset automatically in fetch_and_build_embed
        self.page += 1
        await self.update_message(interaction)


class CurrentLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="current_leaderboard",
        description="Shows the current Global Legend League leaderboard (top 200)"
    )
    async def current_leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        view = LeaderboardView(self.bot)
        embed = await view.fetch_and_build_embed()
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(CurrentLeaderboard(bot))

