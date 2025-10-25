import discord
from discord.ext import commands
import config
from utils.logging import send_log
import time

class AntiRaidCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_log = []

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != config.GUILD_ID:
            return
        now = time.time()
        self.join_log = [t for t in self.join_log if now - t < 10]
        self.join_log.append(now)
        if len(self.join_log) > 10:
            log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send("🚨 **ALERTE RAID** détecté !")
            embed = discord.Embed(
                title="🚨 RAID DÉTECTÉ",
                description=f"{len(self.join_log)} membres en 10 secondes.",
                color=0xff0000,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "threats", embed)

async def setup(bot):
    await bot.add_cog(AntiRaidCog(bot))