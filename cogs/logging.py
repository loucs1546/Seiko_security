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

        deleter = None
        try:
            # Cherche d'abord des entrées message_delete
            async for entry in message.guild.audit_logs(limit=10, action=discord.AuditLogAction.message_delete):
                # entry.target peut être l'utilisateur dont le message a été supprimé
                if entry.target and getattr(entry.target, "id", None) == message.author.id:
                    extra = getattr(entry, "extra", None)
                    channel = getattr(extra, "channel", None)
                    if channel and channel.id != message.channel.id:
                        continue
                    if (discord.utils.utcnow() - entry.created_at).total_seconds() < 6:
                        deleter = entry.user
                        break

            # Si rien trouvé, vérifier les suppressions en masse (bulk)
            if deleter is None:
                async for entry in message.guild.audit_logs(limit=10, action=discord.AuditLogAction.message_bulk_delete):
                    extra = getattr(entry, "extra", None)
                    channel = getattr(extra, "channel", None)
                    if channel and channel.id == message.channel.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 6:
                        deleter = entry.user
                        break

        except discord.Forbidden:
            # Permission manquante : VIEW_AUDIT_LOG
            deleter = None
        except Exception:
            # Ne pas échouer si audit_logs plante pour une raison inattendue
            deleter = None

        if deleter is None:
            # Si on n'a pas pu déterminer le modérateur, indiquer clairement pourquoi possible
            description = (
                f"**Auteur** : {message.author.mention}\n"
                f"**Salon** : {message.channel.mention}\n"
                f"**Supprimé par** : Inconnu (vérifie la permission 'View Audit Log' du bot ou délai de détection)"
            )
        else:
            description = (
                f"**Auteur** : {message.author.mention}\n"
                f"**Salon** : {message.channel.mention}\n"
                f"**Supprimé par** : {deleter.mention}"
            )

        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=description,
            color=0xff8800,
            timestamp=discord.utils.utcnow()
        )
        if message.content:
            embed.add_field(name="Contenu", value=message.content[:1020], inline=False)
        await send_log(self.bot, "messages", embed)


    # --- on_voice_state_update (parties mute/deaf et déplacement) ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.guild.id != config.GUILD_ID:
            return

        # Déplacement vocal
        if before.channel and after.channel and before.channel != after.channel:
            moderator = None
            try:
                async for entry in member.guild.audit_logs(limit=10, action=discord.AuditLogAction.member_move):
                    if entry.target and entry.target.id == member.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 6:
                        moderator = entry.user
                        break
            except discord.Forbidden:
                moderator = None
            except Exception:
                moderator = None

            description = f"{member.mention} : {before.channel.mention} → {after.channel.mention}"
            if moderator:
                description += f"\n**Déplacé par** : {moderator.mention}"
            else:
                description += "\n**Déplacé par** : Inconnu (vérifie la permission 'View Audit Log')"

            embed = discord.Embed(
                title="🎤 Déplacement vocal",
                description=description,
                color=0xffff00,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "vocal", embed)
            return

        # Mute / Unmute ou Deaf / Undeaf
        if before.mute != after.mute or before.deaf != after.deaf:
            moderator = None
            try:
                async for entry in member.guild.audit_logs(limit=10, action=discord.AuditLogAction.member_update):
                    if not entry.target or entry.target.id != member.id:
                        continue
                    # entry.changes peut être soit un dict soit un objet ; on le traite prudemment
                    changes = getattr(entry, "changes", {})
                    mute_change = None
                    deaf_change = None
                    if isinstance(changes, dict):
                        mute_change = changes.get("mute")
                        deaf_change = changes.get("deaf")
                    else:
                        mute_change = getattr(changes, "mute", None)
                        deaf_change = getattr(changes, "deaf", None)

                    time_ok = (discord.utils.utcnow() - entry.created_at).total_seconds() < 6
                    mute_cond = (before.mute != after.mute and mute_change is not None)
                    deaf_cond = (before.deaf != after.deaf and deaf_change is not None)
                    if time_ok and (mute_cond or deaf_cond):
                        moderator = entry.user
                        break
            except discord.Forbidden:
                moderator = None
            except Exception:
                moderator = None

            actions = []
            if before.mute != after.mute:
                actions.append("mute vocal" if after.mute else "unmute vocal")
            if before.deaf != after.deaf:
                actions.append("sourdine" if after.deaf else "fin de sourdine")

            description = f"{member.mention} — {', '.join(actions)}"
            if moderator:
                description += f"\n**Modifié par** : {moderator.mention}"
            else:
                description += "\n**Modifié par** : Inconnu (vérifie la permission 'View Audit Log')"

            embed = discord.Embed(
                title="🎤 État vocal modifié",
                description=description,
                color=0x1abc9c,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "vocal", embed)
            return

        # Connexion ou déconnexion (reste inchangé)
        if before.channel is None and after.channel:
            embed = discord.Embed(
                title="🎤 Connexion vocale",
                description=f"{member.mention} a rejoint {after.channel.mention}",
                color=0x00ff00,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "vocal", embed)
        elif before.channel and after.channel is None:
            embed = discord.Embed(
                title="🎤 Déconnexion vocale",
                description=f"{member.mention} a quitté {before.channel.mention}",
                color=0xff0000,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "vocal", embed)


    # --- on_member_update (gestion des changements de rôles) ---
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.guild.id != config.GUILD_ID:
            return

        # Pseudo / avatar (inchangé ici)...
        if before.nick != after.nick:
            # (conserve ta logique existante pour les pseudos)
            moderator = None
            try:
                async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                    if (
                        entry.target and entry.target.id == after.id and
                        hasattr(entry.changes, 'nick') and
                        entry.changes.nick[0] == before.nick and
                        entry.changes.nick[1] == after.nick and
                        (discord.utils.utcnow() - entry.created_at).total_seconds() < 6
                    ):
                        moderator = entry.user
                        break
            except:
                moderator = None

            old_nick = before.nick or before.global_name or before.name
            new_nick = after.nick or after.global_name or after.name
            description = f"{after.mention}"
            if moderator:
                description += f"\n**Modifié par** : {moderator.mention}"
            else:
                description += "\n**Modifié par** : Inconnu (vérifie la permission 'View Audit Log')"

            embed = discord.Embed(
                title="📛 Pseudo modifié",
                description=description,
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Avant", value=old_nick, inline=True)
            embed.add_field(name="Après", value=new_nick, inline=True)
            await send_log(self.bot, "profile", embed)

        # Changement d'avatar (inchangé)
        if before.avatar != after.avatar:
            embed = discord.Embed(
                title="🖼️ Avatar modifié",
                description=f"{after.mention}",
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            embed.set_thumbnail(url=after.display_avatar.url)
            await send_log(self.bot, "profile", embed)

        # Rôles ajoutés/enlevés
        before_roles = set(before.roles)
        after_roles = set(after.roles)
        if before_roles != after_roles:
            moderator = None
            try:
                async for entry in after.guild.audit_logs(limit=10, action=discord.AuditLogAction.member_role_update):
                    if entry.target and entry.target.id == after.id and (discord.utils.utcnow() - entry.created_at).total_seconds() < 6:
                        moderator = entry.user
                        break
            except discord.Forbidden:
                moderator = None
            except Exception:
                moderator = None

            added = after_roles - before_roles
            removed = before_roles - after_roles
            parts = []
            if added:
                parts.append("Ajoutés : " + ", ".join(r.mention for r in added))
            if removed:
                parts.append("Retirés : " + ", ".join(r.mention for r in removed))

            description = f"{after.mention}\n" + ("\n".join(parts) if parts else "")
            if moderator:
                description += f"\n**Modifié par** : {moderator.mention}"
            else:
                description += "\n**Modifié par** : Inconnu (vérifie la permission 'View Audit Log')"

            embed = discord.Embed(
                title="🔧 Rôles modifiés",
                description=description,
                color=0x00ccff,
                timestamp=discord.utils.utcnow()
            )
            await send_log(self.bot, "profile", embed)

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