# cogs/logging.py
import discord
from discord.ext import commands
from discord import app_commands
from utils.logging import send_log_to
import datetime
import core_config as config
from utils.logging import send_log

class LogSetupModal(discord.ui.Modal):
    def __init__(self, log_type):
        super().__init__(title=f"Configuration des logs {log_type}")
        self.log_type = log_type
        self.channel = discord.ui.TextInput(
            label="ID du salon",
            placeholder="Entrez l'ID du salon pour ces logs",
            required=True
        )
        self.add_item(self.channel)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            channel_id = int(self.channel.value)
            config.CONFIG.setdefault("logs", {})[self.log_type] = channel_id
            await interaction.response.send_message(
                f"✅ Logs {self.log_type} configurés dans <#{channel_id}>",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(
                "❌ ID de salon invalide",
                ephemeral=True
            )

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_to_channel(self, log_type: str, embed: discord.Embed):
        if not isinstance(config.CONFIG, dict) or "logs" not in config.CONFIG:
            return
        
        channel_id = config.CONFIG["logs"].get(log_type)
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Erreur d'envoi de log: {e}")

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

    async def _dump_recent_audit_entries(self, guild, limit=12):
        """Utilitaire de debug : renvoie une liste d'info sur les dernières entrées d'audit"""
        rows = []
        try:
            async for entry in guild.audit_logs(limit=limit):
                extra = getattr(entry, "extra", None)
                rows.append({
                    "action": getattr(entry.action, "name", str(entry.action)),
                    "user": getattr(entry.user, "id", None),
                    "user_name": getattr(entry.user, "name", None) if entry.user else None,
                    "target": getattr(entry.target, "id", None) if entry.target else None,
                    "target_repr": repr(entry.target),
                    "created_at": entry.created_at.isoformat() if entry.created_at else None,
                    "extra": repr(extra)
                })
        except Exception as e:
            rows.append({"error": repr(e)})
        return rows

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.guild.id != config.GUILD_ID or message.author.bot:
            return

        deleter = None
        try:
            # Cherche des entrées message_delete
            async for entry in message.guild.audit_logs(limit=50, action=discord.AuditLogAction.message_delete):
                # Plusieurs possibilités selon la structure :
                # - entry.target peut être l'utilisateur dont le message a été supprimé
                # - entry.extra peut contenir le channel, count, voire le message id selon la version de discord/discord.py
                target_id = getattr(entry.target, "id", None) if entry.target else None
                extra = getattr(entry, "extra", None)
                extra_channel = getattr(extra, "channel", None) if extra else None
                # Tentatives de matching :
                match_author = (target_id == message.author.id)
                match_channel = (extra_channel and getattr(extra_channel, "id", None) == message.channel.id)
                # Certaines implémentations fournissent un message_id dans extra
                extra_message_id = getattr(extra, "message_id", None) if extra else None
                match_message_id = (extra_message_id == message.id) if extra_message_id else False

                age = (discord.utils.utcnow() - entry.created_at).total_seconds() if entry.created_at else 9999
                if (match_author or match_channel or match_message_id) and age < 30:
                    deleter = entry.user
                    break

            # Si pas trouvé, tenter message_bulk_delete
            if deleter is None:
                async for entry in message.guild.audit_logs(limit=20, action=discord.AuditLogAction.message_bulk_delete):
                    extra = getattr(entry, "extra", None)
                    extra_channel = getattr(extra, "channel", None) if extra else None
                    count = getattr(extra, "count", None) if extra else None
                    age = (discord.utils.utcnow() - entry.created_at).total_seconds() if entry.created_at else 9999
                    if extra_channel and getattr(extra_channel, "id", None) == message.channel.id and age < 30:
                        deleter = entry.user
                        break

        except discord.Forbidden:
            # Pas la permission VIEW_AUDIT_LOG (ou bot limité) — on garde deleter = None
            deleter = None
        except Exception:
            # Ne pas tout casser en prod
            deleter = None

        if deleter is None:
            # Si on n'a pas trouvé, dump les dernières entrées d'audit dans la console / log pour debug.
            dump = await self._dump_recent_audit_entries(message.guild, limit=12)
            # Envoie le dump dans la console (ou dans un salon de debug si tu préfères)
            self.bot.logger = getattr(self.bot, "logger", None)
            if self.bot.logger:
                self.bot.logger.warning("Audit dump for message_delete: %s", dump)
            else:
                print("Audit dump for message_delete:", dump)

            description = (
                f"**Auteur** : {message.author.mention}\n"
                f"**Salon** : {message.channel.mention}\n"
                f"**Supprimé par** : Inconnu (voir debug audit dump dans la console ou log)"
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
        try:
            if interaction.command:
                full_command = f"/{interaction.command.name}"
                if interaction.command.parent:
                    full_command = f"/{interaction.command.parent.name} {interaction.command.name}"
            else:
                full_command = "unknown command"
                
            # Log l'utilisation de la commande
            embed = discord.Embed(
                title="🤖 Commande utilisée",
                description=f"**Commande**: {full_command}\n**Utilisateur**: {interaction.user.mention}",
                color=0x00ff00
            )
            await send_log_to(self.bot, "messages", embed)
        except Exception as e:
            print(f"Erreur logging commande: {e}")

    @app_commands.command(name="logs")
    @app_commands.describe(type="Type de logs à configurer")
    @app_commands.choices(type=[
        app_commands.Choice(name="Messages", value="messages"),
        app_commands.Choice(name="Modération", value="moderation"),
        app_commands.Choice(name="Tickets", value="ticket"),
        app_commands.Choice(name="Vocal", value="vocal"),
        app_commands.Choice(name="Giveaway", value="giveaway"),
        app_commands.Choice(name="Sécurité", value="securite")
    ])
    async def configure_logs(self, interaction: discord.Interaction, type: str):
        await interaction.response.send_modal(LogSetupModal(type))

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))