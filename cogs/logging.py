# cogs/logging.py
import discord
from discord.ext import commands
import config

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != config.GUILD_ID:
            return
        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="📥 Nouveau membre",
                description=f"{member.mention} (`{member.id}`) a rejoint le serveur.",
                color=0x00ff00,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != config.GUILD_ID:
            return
        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="📤 Membre parti",
                description=f"{member.mention} (`{member.id}`) a quitté le serveur.",
                color=0xff0000,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await log_channel.send(embed=embed)

# ⬇️ Fonction OBLIGATOIRE pour charger le cog
async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
