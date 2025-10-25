import discord
from discord.ext import commands
import config
from utils.db import supabase_insert
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
            await supabase_insert("logs", {
                "guild_id": config.GUILD_ID,
                "user_id": uid,
                "action": "spam_blocked",
                "details": {"content": message.content[:100]}
            })

async def setup(bot):
    await bot.add_cog(AntiSpamCog(bot))
