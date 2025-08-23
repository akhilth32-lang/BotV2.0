# extensions/leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans, to_regular_gg_sans
from datetime import datetime, timezone, timedelta

LEADERBOARD_PAGE_SIZE = 20

# Dummy legend seasons data example (replace with your actual data)
LEGEND_SEASONS_2025 = [
    {"start": datetime(2025, 7, 1, tzinfo=timezone.utc), "end": datetime(2025, 7, 29, tzinfo=timezone.utc), "duration_days": 28},
]

def get_legend_day_info(day_offset=0):
    now = datetime.now(timezone.utc)
    for season in LEGEND_SEASONS_2025:
        if season["start"] <= now < season["end"]:
            season_start = season["start"]
            target_day = season_start + timedelta(days=day_offset)
            elapsed = (target_day - season_start).days + 1
            total = season["duration_days"]
            season_month = season_start.strftime("%Y-%m")
            local_now = now.astimezone()
            return elapsed, total, season_month, local_now
    # fallback
    local_now = now.astimezone()
    return None, None, None, local_now

class LeaderboardView(discord.ui.View):
    def __init__(self, sorted_players, leaderboard_name, embed_color, snapshot_day):
        super().__init__(timeout=600)
        self.sorted_players = sorted_players
        self.page = 1
        self.leaderboard_name = leaderboard_name
        self.total_pages = (len(sorted_players) + LEADERBOARD_PAGE_SIZE - 1) // LEADERBOARD_PAGE_SIZE
        self.embed_color = embed_color
        self.snapshot_day = snapshot_day

    def build_embed(self):
        start = (self.page - 1) * LEADERBOARD_PAGE_SIZE
        end = start + LEADERBOARD_PAGE_SIZE
        page_players = self.sorted_players[start:end]

        description_lines = []
        rank_offset = start
        for idx, player in enumerate(page_players, start=1):
            rank = rank_offset + idx
            name = to_bold_gg_sans(player.get("player_name", "Unknown"))
            tag = player.get("player_tag", "N/A")
            trophies = player.get("trophies", 0)

            offense_change = player.get("offense_trophies_change", 0)
            offense_attacks = player.get("offense_attacks", 0)
            defense_change = player.get("defense_trophies_change", 0)
            defense_defends = player.get("defense_defends", 0)

            offense_display = f"{EMOJIS['offense']} {offense_change:+}/{offense_attacks}"
            defense_display = f"{EMOJIS['defense']} {defense_change:+}/{defense_defends}"

            line = f"{rank}. {name} ({tag})\n   🏆 {trophies} | {offense_display} | {defense_display}"
            description_lines.append(line)
            description_lines.append("")  # Small spacing between players

        embed = create_embed(
            title=f"Linked Players Leaderboard - {self.leaderboard_name}",
            description="\n".join(description_lines),
            color=discord.Color(int(self.embed_color.replace("#", ""), 16))
        )

        elapsed, total, season_month, local_now = get_legend_day_info(self.snapshot_day)
        if elapsed and total and season_month:
            footer_text = f"Day {elapsed}/{total} ({season_month}) | Today at {local_now.strftime('%I:%M %p')}"
        else:
            footer_text = f"Day info unavailable | {local_now.strftime('%m/%d/%Y %I:%M %p')}"

        embed.set_footer(text=footer_text + f" | Page {self.page}/{self.total_pages}")
        return embed

    async def update_message(self, interaction):
        embed = self.build_embed()
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
        await interaction.response.defer()
        # Optional: Refresh data from DB here if needed
        await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.total_pages:
            self.page += 1
            await self.update_message(interaction)
        else:
            await interaction.response.send_message("You are already on the last page.", ephemeral=True)

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Show leaderboard of all linked Clash of Clans player accounts")
    @app_commands.describe(
        leaderboard_name="Enter leaderboard name to filter (optional)",
        color="Embed hex color, e.g. #000000 (optional, default black)",
        day="Legend league day snapshot (0=current day)"
    )
    async def leaderboard(self, interaction: discord.Interaction, leaderboard_name: str = "All", color: str = "#000000", day: int = 0):
        await interaction.response.defer()

        all_players = await player_crud.get_all_linked_players()

        if leaderboard_name != "All":
            filtered_players = [p for p in all_players if p.get("leaderboard_name", "").lower() == leaderboard_name.lower()]
        else:
            filtered_players = all_players

        sorted_players = sorted(filtered_players, key=lambda p: p.get('trophies', 0), reverse=True)

        if not sorted_players:
            await interaction.followup.send("No players found for the specified leaderboard.")
            return

        view = LeaderboardView(sorted_players, leaderboard_name, color, day)
        embed = view.build_embed()
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
    
