from discord.ext import commands
from database.player_crud import get_player_by_tag, create_player, update_player_by_tag

class Link(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="link")
    async def link_command(self, ctx, player_tag: str, api_token: str):
        """Link a Clash of Clans player with Discord user, storing player tag and API token."""
        
        player = get_player_by_tag(player_tag)
        if player:
            # Update existing player with new Discord ID and API token
            update_player_by_tag(player_tag, {
                "discord_id": str(ctx.author.id),
                "api_token": api_token
            })
            await ctx.send(f"Updated and linked player {player_tag} to your Discord account.")
        else:
            # Create new player entry with API token and Discord ID
            player_data = {
                "tag": player_tag,
                "discord_id": str(ctx.author.id),
                "api_token": api_token
            }
            create_player(player_data)
            await ctx.send(f"Created and linked player {player_tag} to your Discord account.")

async def setup(bot):
    await bot.add_cog(Link(bot))
    
