import discord
from discord.ext import commands
import config
from utils.logging import send_log

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not after.guild or after.guild.id != config.GUILD_ID or after.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="✏️ Message édité",
            description=f"Par {after.author.mention} dans {after.channel.mention}",
            color=0xffff00,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="Avant", value=before.content[:1020] or "*(vide)*", inline=False)
        embed.add_field(name="Après", value=after.content[:1020] or "*(vide)*", inline=False)
        await send_log(self.bot, "messages", embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID or message.author.bot:
            return
        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=f"Par {message.author.mention} dans {message.channel.mention}",
            color=0xff8800,
            timestamp=discord.utils.utcnow()
        )
        if message.content:
            embed.add_field(name="Contenu", value=message.content[:1020], inline=False)
        await send_log(self.bot, "messages", embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id != config.GUILD_ID:
            return

        # Changement de pseudo
        if before.nick != after.nick:
            embed = discord.Embed(
                title="📛 Pseudo modifié",
                description=f"{after.mention}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Avant", value=before.nick or "Aucun", inline=True)
            embed.add_field(name="Après", value=after.nick or "Aucun", inline=True)
            await send_log(self.bot, "profile", embed)

        # Changement d'avatar
        if before.avatar != after.avatar:
            embed = discord.Embed(
                title="🖼️ Avatar modifié",
                description=f"{after.mention}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            await send_log(self.bot, "profile", embed)

        # Changement de rôles
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        if before_roles != after_roles:
            added = after_roles - before_roles
            removed = before_roles - after_roles
            desc = ""
            if added:
                desc += "➕ Ajoutés : " + ", ".join(r.mention for r in added) + "\n"
            if removed:
                desc += "➖ Retirés : " + ", ".join(r.mention for r in removed)
            if desc:
                embed = discord.Embed(
                    title="👑 Rôles modifiés",
                    description=f"{after.mention}\n{desc}",
                    color=0xffaa00,
                    timestamp=discord.utils.utcnow()
                )
                await send_log(self.bot, "roles", embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != config.GUILD_ID:
            return

        embed = None
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎤 Connexion vocale",
                description=f"{member.mention} a rejoint {after.channel.mention}",
                color=0x00ff00
            )
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🎤 Déconnexion vocale",
                description=f"{member.mention} a quitté {before.channel.mention}",
                color=0xff0000
            )
        elif before.channel != after.channel:
            embed = discord.Embed(
                title="🎤 Changement de salon vocal",
                description=f"{member.mention} : {before.channel.mention} → {after.channel.mention}",
                color=0xffff00
            )

        if embed:
            embed.timestamp = discord.utils.utcnow()
            await send_log(self.bot, "vocal", embed)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
