# extensions/leaderboard.py

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, button
from database import player_crud
from config.emoji import EMOJIS
from utils.embed_helpers import create_embed
from config.fonts import to_bold_gg_sans
from config.legend_season import get_legend_day_info

LEADERBOARD_PAGE_SIZE = 20


class LeaderboardView(View):
    def __init__(self, cog, interaction, players, color, day, name, page=1):
        super().__init__(timeout=120)  # 2 min timeout
        self.cog = cog
        self.interaction = interaction
        self.players = players
        self.color = color
        self.day = day
        self.name = name
        self.page = page
        self.total_pages = (len(players) + LEADERBOARD_PAGE_SIZE - 1) // LEADERBOARD_PAGE_SIZE

    def build_embed(self):
        # Paginate players
        start = (self.page - 1) * LEADERBOARD_PAGE_SIZE
        end = start + LEADERBOARD_PAGE_SIZE
        page_players = self.players[start:end]

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

            # Add small spacing between players
            line = (
                f"{rank}. {name} ({tag})\n"
                f"   🏆 {trophies} | {offense_display} | {defense_display}\n"
            )
            description_lines.append(line)

        embed = create_embed(
            title=self.name,
            description="\n".join(description_lines),
            color=discord.Color(int(self.color.replace('#', ''), 16))
        )

        # Legend day info (current or chosen snapshot)
        day_info = get_legend_day_info(self.day)
        embed.set_footer(
            text=f"Day {day_info['day_number']}/{day_info['total_days']} "
                 f"({day_info['season']}) | Today at {discord.utils.format_dt(discord.utils.utcnow(), 't')}"
        )

        return embed

    async def update_message(self, interaction):
        embed = self.build_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @button(label="⬅ Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 1:
            self.page -= 1
        await self.update_message(interaction)

    @button(label="🔄 Refresh", style=discord.ButtonStyle.success)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Refetch latest players
        all_players = await player_crud.get_all_linked_players()
        self.players = sorted(all_players, key=lambda p: p.get('trophies', 0), reverse=True)
        self.total_pages = (len(self.players) + LEADERBOARD_PAGE_SIZE - 1) // LEADERBOARD_PAGE_SIZE
        await self.update_message(interaction)

    @button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.total_pages:
            self.page += 1
        await self.update_message(interaction)


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="leaderboard",
        description="Show leaderboard of all linked Clash of Clans player accounts"
    )
    @app_commands.describe(
        color="Embed color in hex (e.g. #000000 for black, default black)",
        day="Legend league day snapshot to view (default current day)",
        name="Leaderboard title (default 'Linked Players Leaderboard')"
    )
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        color: str = "#000000",
        day: int = 0,
        name: str = "Linked Players Leaderboard"
    ):
        await interaction.response.defer()

        # Fetch linked players sorted by trophies
        all_players = await player_crud.get_all_linked_players()
        sorted_players = sorted(all_players, key=lambda p: p.get('trophies', 0), reverse=True)

        # Build interactive view
        view = LeaderboardView(self, interaction, sorted_players, color, day, name, page=1)
        embed = view.build_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
