# cogs/logging.py
import discord
from discord.ext import commands
import core_config as config
from utils.logging import send_log

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_audit_author(self, guild, target_id, action_type, max_age_seconds=15):
        try:
            async for entry in guild.audit_logs(action=action_type, limit=10):
                if entry.target.id == target_id and (discord.utils.utcnow() - entry.created_at).total_seconds() < max_age_seconds:
                    return entry.user
        except Exception:
            pass
        return None

    async def get_voice_action_author(self, guild, target_id, max_age_seconds=15):
        """Récupère l'auteur d'une action vocale (déplacement, déconnexion) en vérifiant plusieurs types de logs."""
        try:
            async for entry in guild.audit_logs(limit=10):
                if entry.target.id != target_id:
                    continue
                if (discord.utils.utcnow() - entry.created_at).total_seconds() > max_age_seconds:
                    continue
                # Vérifie les actions vocales connues
                if entry.action in (
                    discord.AuditLogAction.member_disconnect,
                    discord.AuditLogAction.member_move
                ):
                    return entry.user
                # Vérifie aussi member_update avec changement de salon vocal (cas rare)
                if entry.action == discord.AuditLogAction.member_update:
                    if hasattr(entry.changes, 'channel_id'):
                        return entry.user
        except Exception:
            pass
        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID or message.author.id == self.bot.user.id:
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
            description=f"**Auteur** : {message.author.mention}\n**Salon** : {message.channel.mention}",
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
            moderator = await self.get_audit_author(
                after.guild,
                after.id,
                discord.AuditLogAction.member_update,
                max_age_seconds=15
            )
            fait_par = moderator.mention if moderator else "Inconnu"

            old_nick = before.nick or before.global_name or before.name
            new_nick = after.nick or after.global_name or after.name

            embed = discord.Embed(
                title="📛 Pseudo modifié",
                description=f"{after.mention}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Avant", value=old_nick, inline=True)
            embed.add_field(name="Après", value=new_nick, inline=True)
            embed.add_field(name="Fait par", value=fait_par, inline=False)
            await send_log(self.bot, "profile", embed)

        if before.avatar != after.avatar:
            embed = discord.Embed(
                title="🖼️ Avatar modifié",
                description=f"{after.mention}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            await send_log(self.bot, "profile", embed)

        before_roles = set(before.roles)
        after_roles = set(after.roles)
        if before_roles != after_roles:
            moderator = await self.get_audit_author(
                after.guild,
                after.id,
                discord.AuditLogAction.member_role_update,
                max_age_seconds=15
            )
            fait_par = moderator.mention if moderator else "Inconnu"

            added = after_roles - before_roles
            removed = before_roles - after_roles
            desc = ""
            if added: desc += "➕ Ajoutés : " + ", ".join(r.mention for r in added) + "\n"
            if removed: desc += "➖ Retirés : " + ", ".join(r.mention for r in removed)
            if desc:
                embed = discord.Embed(
                    title="👑 Rôles modifiés",
                    description=f"{after.mention}\n{desc}**Fait par** : {fait_par}",
                    color=0xffaa00,
                    timestamp=discord.utils.utcnow()
                )
                await send_log(self.bot, "roles", embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != config.GUILD_ID:
            return

        # Fonction pour obtenir l'auteur d'une action vocale récente
        async def get_voice_moderator(guild, action_time):
            try:
                async for entry in guild.audit_logs(limit=5):
                    # Vérifie que l'action est récente (±2 secondes)
                    if abs((entry.created_at - action_time).total_seconds()) > 2:
                        continue

                    # Vérifie le type d'action
                    if entry.action in (
                        discord.AuditLogAction.member_move,
                        discord.AuditLogAction.member_disconnect
                    ):
                        return entry.user

                    # Pour member_update, vérifie s'il y a un changement de channel
                    if entry.action == discord.AuditLogAction.member_update:
                        if hasattr(entry.changes, 'channel_id'):
                            return entry.user

            except Exception:
                pass
            return None

        now = discord.utils.utcnow()

        # --- Connexion ---
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎤 Connexion vocale",
                description=f"{member.mention} a rejoint {after.channel.mention}\n**Fait par** : {member.mention}",
                color=0x00ff00,
                timestamp=now
            )
            await send_log(self.bot, "vocal", embed)

        # --- Déconnexion ---
        elif before.channel is not None and after.channel is None:
            moderator = await get_voice_moderator(member.guild, now)
            fait_par = moderator.mention if moderator else member.mention
            embed = discord.Embed(
                title="🎤 Déconnexion vocale",
                description=f"{member.mention} a quitté {before.channel.mention}\n**Fait par** : {fait_par}",
                color=0xff0000,
                timestamp=now
            )
            await send_log(self.bot, "vocal", embed)

        # --- Déplacement ---
        elif before.channel and after.channel and before.channel != after.channel:
            moderator = await get_voice_moderator(member.guild, now)
            fait_par = moderator.mention if moderator else member.mention
            embed = discord.Embed(
                title="🎤 Déplacement vocal",
                description=f"{member.mention} : {before.channel.mention} → {after.channel.mention}\n**Fait par** : {fait_par}",
                color=0xffff00,
                timestamp=now
            )
            await send_log(self.bot, "vocal", embed)

        # --- Mute / Deafen ---
        elif before.mute != after.mute or before.deaf != after.deaf:
            moderator = None
            try:
                async for entry in member.guild.audit_logs(action=discord.AuditLogAction.member_update, limit=5):
                    if abs((entry.created_at - now).total_seconds()) <= 2:
                        if (before.mute != after.mute and getattr(entry.changes, 'mute', None)) or \
                        (before.deaf != after.deaf and getattr(entry.changes, 'deaf', None)):
                            moderator = entry.user
                            break
            except:
                pass
            fait_par = moderator.mention if moderator else "Inconnu"
            actions = []
            if before.mute != after.mute:
                actions.append("mute vocal" if after.mute else "unmute vocal")
            if before.deaf != after.deaf:
                actions.append("sourdine" if after.deaf else "fin de sourdine")
            embed = discord.Embed(
                title="🎤 État vocal modifié",
                description=f"{member.mention} — {', '.join(actions)}\n**Fait par** : {fait_par}",
                color=0x1abc9c,
                timestamp=now
            )
            await send_log(self.bot, "vocal", embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if not interaction.guild or interaction.guild.id != config.GUILD_ID or interaction.type != discord.InteractionType.application_command:
            return

        args = []
        if interaction.data.get("options"):
            for opt in interaction.data["options"]:
                if opt["type"] in (6, 7, 8):
                    args.append(f"{opt['name']}: <@{opt['value']}>")
                else:
                    args.append(f"{opt['name']}: {opt['value']}")

        full_command = f"/{interaction.command.name}"
        if args:
            full_command += " " + " ".join(args)

        embed = discord.Embed(
            title="🛠️ Commande slash détectée",
            description=f"**Utilisateur** : {interaction.user.mention}\n"
                        f"**Commande complète** :\n```\n{full_command}\n```",
            color=0x2ecc71,
            timestamp=discord.utils.utcnow()
        )
        await send_log(self.bot, "commands", embed)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))