import discord
from discord.ext import commands
import config
from utils.db import supabase_insert

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_action(self, action: str, user_id: int = None, target_id: int = None, details: dict = None):
        await supabase_insert("logs", {
            "guild_id": config.GUILD_ID,
            "user_id": user_id,
            "target_id": target_id,
            "action": action,
            "details": details or {}
        })

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != config.GUILD_ID:
            return
        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="📥 Nouveau membre", description=f"{member.mention} a rejoint.", color=0x00ff00)
            await log_channel.send(embed=embed)
        await self.log_action("member_join", user_id=member.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.guild.id != config.GUILD_ID:
            return
        # Les cogs antispam et link_filter géreront les actions
        await self.log_action("message_sent", user_id=message.author.id, details={"content": message.content[:200]})

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
