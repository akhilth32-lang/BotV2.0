# extensions/day_leaderboard.py
import discord
from discord import app_commands, ui, Interaction, Embed
from discord.ext import commands
from config.settings import DAY_LEADERBOARD_PAGE_SIZE, IST_OFFSET_HOURS, IST_OFFSET_MINUTES
from datetime import datetime, timedelta
import aiohttp


class DayLeaderboardView(ui.View):
    def __init__(self, players, color, title, page=0):
        super().__init__(timeout=None)
        self.players = players
        self.color = color
        self.title = title
        self.page = page

    def get_embed(self):
        start = self.page * DAY_LEADERBOARD_PAGE_SIZE
        end = start + DAY_LEADERBOARD_PAGE_SIZE
        embed = Embed(title=self.title, color=self.color)

        now_ist = datetime.utcnow() + timedelta(hours=IST_OFFSET_HOURS, minutes=IST_OFFSET_MINUTES)
        embed.set_footer(text=f"Last refreshed: {now_ist.strftime('%d-%m-%Y %I:%M %p')}")

        for i, p in enumerate(self.players[start:end], start=start + 1):
            embed.add_field(
                name=f"{i}. {p['name']} (#{p['tag']})",
                value=f"🏆 {p['trophies']} | Town Hall: {p.get('townhall', 'N/A')}\n\u200b",
                inline=False
            )
        return embed

    @ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction: Interaction, button: ui.Button):
        if self.page > 0:
            self.page -= 1
            await self.update_message(interaction)

    @ui.button(label="➡️ Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: Interaction, button: ui.Button):
        if (self.page + 1) * DAY_LEADERBOARD_PAGE_SIZE < len(self.players):
            self.page += 1
            await self.update_message(interaction)

    async def update_message(self, interaction: Interaction):
        await interaction.response.defer()
        await interaction.edit_original_response(embed=self.get_embed(), view=self)


class DayLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = 0x118EF5  # Your hex #118ef5 converted

    @app_commands.command(name="leaderboarddaystart", description="Shows EOD snapshot of Legend league leaderboard")
    async def leaderboard_daystart(self, interaction: Interaction):
        await interaction.response.defer()
        url = "https://api.clashk.ing/ranking/live/legends?top_ranking=1&lower_ranking=200"
        async with aiohttp.ClientSession() as session:
            try:
                resp = await session.get(url)
                if resp.status != 200:
                    await interaction.followup.send("Failed to fetch leaderboard data.", ephemeral=True)
                    return
                data = await resp.json()
            except Exception:
                await interaction.followup.send("Failed to fetch leaderboard data.", ephemeral=True)
                return

        # data is list of player objects
        players = data
        title = "🎯 Legend League Day-Start Leaderboard"
        view = DayLeaderboardView(players, self.color, title)
        await interaction.followup.send(embed=view.get_embed(), view=view)


async def setup(bot):
    await bot.add_cog(DayLeaderboard(bot))
    
