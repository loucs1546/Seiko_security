import discord
from discord.ext import commands
import config
from utils.logging import send_log
from collections import defaultdict
import time

class AntiSpamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(list)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.guild.id != config.GUILD_ID:
            return
        uid = message.author.id
        now = time.time()
        self.user_messages[uid] = [t for t in self.user_messages[uid] if now - t < 5]
        self.user_messages[uid].append(now)
        if len(self.user_messages[uid]) > 5:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, ne spammez pas.", delete_after=5)
            embed = discord.Embed(
                title="🚫 SPAM BLOQUÉ",
                description=f"Par {message.author.mention}",
                color=0xff0000,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Contenu", value=message.content[:1020])
            await send_log(self.bot, "threats", embed)

async def setup(bot):
    await bot.add_cog(AntiSpamCog(bot))