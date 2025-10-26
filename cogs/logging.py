# cogs/logging.py
import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            not message.guild or
            message.guild.id != config.GUILD_ID or
            message.author.id == self.bot.user.id  # ← Ignore les messages du bot
        ):
            return

        embed = discord.Embed(
            title="📥 Message reçu",
            description=f"**Auteur** : {message.author.mention}\n**Salon** : {message.channel.mention}\n**Contenu** :\n>>> {message.content or '[Aucun texte]'}",
            color=0x2ecc71,
            timestamp=message.created_at
        )
        if message.attachments:
            urls = "\n".join(a.url for a in message.attachments[:3])
            embed.add_field(name="📎 Pièces jointes", value=urls, inline=False)
        await send_log(self.bot, "messages", embed)

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

        if before.nick != after.nick:
            moderator = "Inconnu"
            try:
                async for entry in after.guild.audit_logs(limit=10, action=discord.AuditLogAction.member_update):
                    if entry.target.id == after.id and hasattr(entry.changes, 'nick') and abs((entry.created_at - discord.utils.utcnow()).total_seconds()) < 15:
                        moderator = entry.user
                        break
            except:
                pass
            old_nick = before.nick or before.global_name or before.name
            new_nick = after.nick or after.global_name or after.name
            embed = discord.Embed(
                title="📛 Pseudo modifié",
                description=f"{after.mention}\n**Modérateur** : {moderator}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Avant", value=old_nick, inline=True)
            embed.add_field(name="Après", value=new_nick, inline=True)
            await send_log(self.bot, "profile", embed)

        before_roles = set(before.roles)
        after_roles = set(after.roles)
        if before_roles != after_roles:
            moderator = "Inconnu"
            try:
                async for entry in after.guild.audit_logs(limit=10, action=discord.AuditLogAction.member_role_update):
                    if entry.target.id == after.id and abs((entry.created_at - discord.utils.utcnow()).total_seconds()) < 15:
                        moderator = entry.user
                        break
            except:
                pass
            added = after_roles - before_roles
            removed = before_roles - after_roles
            desc = ""
            if added: desc += "➕ Ajoutés : " + ", ".join(r.mention for r in added) + "\n"
            if removed: desc += "➖ Retirés : " + ", ".join(r.mention for r in removed)
            if desc:
                embed = discord.Embed(
                    title="👑 Rôles modifiés",
                    description=f"{after.mention}\n**Modérateur** : {moderator}\n{desc}",
                    color=0xffaa00,
                    timestamp=discord.utils.utcnow()
                )
                await send_log(self.bot, "roles", embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != config.GUILD_ID:
            return

        embed = None
        moderator = "Inconnu"

        if before.mute != after.mute or before.deaf != after.deaf:
            try:
                async for entry in member.guild.audit_logs(limit=10, action=discord.AuditLogAction.member_update):
                    if entry.target.id == member.id and abs((entry.created_at - discord.utils.utcnow()).total_seconds()) < 15:
                        if (before.mute != after.mute and getattr(entry.changes, 'mute', None) is not None) or \
                           (before.deaf != after.deaf and getattr(entry.changes, 'deaf', None) is not None):
                            moderator = entry.user
                            break
            except:
                pass
            actions = []
            if before.mute != after.mute: actions.append("mute vocal" if after.mute else "unmute vocal")
            if before.deaf != after.deaf: actions.append("sourdine" if after.deaf else "fin de sourdine")
            embed = discord.Embed(
                title="🎤 État vocal modifié",
                description=f"{member.mention} — {', '.join(actions)}\n**Modérateur** : {moderator}",
                color=0x1abc9c,
                timestamp=discord.utils.utcnow()
            )

        elif before.channel and after.channel and before.channel != after.channel:
            try:
                async for entry in member.guild.audit_logs(limit=10, action=discord.AuditLogAction.member_move):
                    if entry.target.id == member.id and abs((entry.created_at - discord.utils.utcnow()).total_seconds()) < 15:
                        moderator = entry.user
                        break
            except:
                pass
            embed = discord.Embed(
                title="🎤 Déplacement vocal",
                description=f"{member.mention} : {before.channel.mention} → {after.channel.mention}" +
                            (f"\n**Modérateur** : {moderator}" if moderator != "Inconnu" else ""),
                color=0xffff00,
                timestamp=discord.utils.utcnow()
            )

        elif before.channel and not after.channel:
            try:
                async for entry in member.guild.audit_logs(limit=10, action=discord.AuditLogAction.member_disconnect):
                    if entry.target.id == member.id and abs((entry.created_at - discord.utils.utcnow()).total_seconds()) < 15:
                        moderator = entry.user
                        break
            except:
                pass
            embed = discord.Embed(
                title="🎤 Déconnexion forcée" if moderator != "Inconnu" else "🎤 Déconnexion vocale",
                description=f"{member.mention} a quitté {before.channel.mention}" +
                            (f"\n**Modérateur** : {moderator}" if moderator != "Inconnu" else ""),
                color=0xff0000,
                timestamp=discord.utils.utcnow()
            )

        elif not before.channel and after.channel:
            embed = discord.Embed(
                title="🎤 Connexion vocale",
                description=f"{member.mention} a rejoint {after.channel.mention}",
                color=0x00ff00,
                timestamp=discord.utils.utcnow()
            )

        if embed:
            await send_log(self.bot, "vocal", embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.guild or interaction.guild.id != config.GUILD_ID:
            return
        if interaction.type == discord.InteractionType.application_command:
            embed = discord.Embed(
                title="🛠️ Commande slash détectée",
                description=f"**Utilisateur** : {interaction.user.mention}\n**Commande** : `/{interaction.command.name}`",
                color=0x2ecc71,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "commands", embed)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))