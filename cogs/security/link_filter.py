import discord
from discord.ext import commands
import config
from utils.db import supabase_insert
import re

URL_REGEX = re.compile(r"https?://[^\s]+")

class LinkFilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild or message.guild.id != config.GUILD_ID:
            return
        if URL_REGEX.search(message.content):
            await supabase_insert("logs", {
                "guild_id": config.GUILD_ID,
                "user_id": message.author.id,
                "action": "link_posted",
                "details": {"url": URL_REGEX.search(message.content).group()}
            })
            # Ici, tu pourrais scanner avec VirusTotal, vérifier contre `threats`, etc.

async def setup(bot):
    await bot.add_cog(LinkFilterCog(bot))
