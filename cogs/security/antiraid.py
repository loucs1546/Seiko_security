import discord
from discord.ext import commands
import config
from utils.db import supabase_insert
import asyncio

class AntiRaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_log = []

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != config.GUILD_ID:
            return
        now = discord.utils.utcnow().timestamp()
        self.join_log = [t for t in self.join_log if now - t < 10]  # fenêtre de 10s
        self.join_log.append(now)
        if len(self.join_log) > 10:  # plus de 10 joins en 10s = raid
            log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send("🚨 **ALERTE RAID** détecté ! Verrouillage du serveur.")
            await supabase_insert("logs", {
                "guild_id": config.GUILD_ID,
                "action": "raid_detected",
                "details": {"join_count": len(self.join_log)}
            })
            # Ici, tu pourrais révoquer les invites, fermer les salons, etc.

async def setup(bot):
    await bot.add_cog(AntiRaidCog(bot))
