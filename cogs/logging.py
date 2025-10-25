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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild and message.guild.id == config.GUILD_ID and not message.author.bot:
            # Tu pourras ajouter ici la détection de liens, spam, etc. plus tard
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.guild or after.guild.id != config.GUILD_ID or after.author.bot:
            return
        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        if log_channel and before.content != after.content:
            embed = discord.Embed(
                title="✏️ Message édité",
                description=f"Par {after.author.mention} dans {after.channel.mention}",
                color=0xffff00,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Avant", value=before.content[:1020] or "*(vide)*", inline=False)
            embed.add_field(name="Après", value=after.content[:1020] or "*(vide)*", inline=False)
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID or message.author.bot:
            return
        log_channel = self.bot.get_channel(config.LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message supprimé",
                description=f"Par {message.author.mention} dans {message.channel.mention}",
                color=0xff8800,
                timestamp=discord.utils.utcnow()
            )
            if message.content:
                embed.add_field(name="Contenu", value=message.content[:1020], inline=False)
            if message.attachments:
                embed.add_field(name="Pièces jointes", value=", ".join([a.url for a in message.attachments]))
            await log_channel.send(embed=embed)