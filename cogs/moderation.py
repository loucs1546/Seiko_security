# cogs/moderation.py
import discord
from discord.ext import commands
import config
from utils.db import supabase_select
import json

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Commande existante : /audit ---
    @discord.app_commands.command(name="audit", description="Analyse la sécurité du serveur")
    async def audit(self, interaction: discord.Interaction):
        issues = []
        guild = interaction.guild
        if not guild.me.guild_permissions.administrator:
            issues.append("Bot sans permissions admin.")
        if any(role.permissions.administrator and not role.managed for role in guild.roles if role != guild.default_role):
            issues.append("Rôles admin non gérés détectés.")
        score = max(0, 100 - len(issues) * 20)
        await interaction.response.send_message(
            f"🔍 **Audit de sécurité**\n**Score** : {score}/100\n**Problèmes** : {', '.join(issues) or 'Aucun'}",
            ephemeral=True
        )

    # --- Commande existante : /purge ---
    @discord.app_commands.command(name="purge")
    @discord.app_commands.describe(limit="Nombre de messages à supprimer")
    async def purge(self, interaction: discord.Interaction, limit: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return
        deleted = await interaction.channel.purge(limit=limit)
        await interaction.response.send_message(f"🧹 **{len(deleted)}** messages supprimés.", ephemeral=True)

    # --- NOUVELLE COMMANDE : /show-data ---
    @discord.app_commands.command(name="show-data", description="Affiche un résumé des données de sécurité du serveur")
    async def show_data(self, interaction: discord.Interaction):
        # 🔒 Sécurité : uniquement pour le propriétaire ou les admins
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Accès réservé aux administrateurs.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)  # Pour éviter le timeout

        try:
            # Récupérer les données
            guilds = await supabase_select("guilds", {"guild_id": str(config.GUILD_ID)})
            users = await supabase_select("users", {"guild_id": str(config.GUILD_ID)})
            logs = await supabase_select("logs", {"guild_id": str(config.GUILD_ID)})
            tickets = await supabase_select("tickets", {"guild_id": str(config.GUILD_ID)})

            guild = guilds[0] if guilds else {}

            # Embed principal
            embed = discord.Embed(
                title="🛡️ **Données de sécurité – Seiko**",
                description=f"Résumé des données stockées pour le serveur <@{config.GUILD_ID}>",
                color=0x00ffcc,
                timestamp=discord.utils.utcnow()
            )

            # Section : Configuration du serveur
            config_text = (
                f"**Logs** : <#{guild.get('log_channel_id', 'N/A')}>\n"
                f"**Anti-Raid** : {'✅' if guild.get('anti_raid_enabled') else '❌'}\n"
                f"**Anti-Spam** : {'✅' if guild.get('anti_spam_enabled') else '❌'}\n"
                f"**Filtre Liens** : {'✅' if guild.get('link_filter_enabled') else '❌'}\n"
                f"**Score** : {guild.get('security_score', 'N/A')}/100\n"
                f"**Verrouillé** : {'🔒 Oui' if guild.get('locked') else '🔓 Non'}"
            )
            embed.add_field(name="⚙️ Configuration", value=config_text, inline=False)

            # Section : Statistiques
            stats_text = (
                f"**Membres suivis** : {len(users)}\n"
                f"**Événements logués** : {len(logs)}\n"
                f"**Tickets actifs** : {len([t for t in tickets if t.get('status') == 'open'])}\n"
                f"**Tickets totaux** : {len(tickets)}"
            )
            embed.add_field(name="📊 Statistiques", value=stats_text, inline=False)

            # Section : Derniers logs (3 derniers)
            if logs:
                recent_logs = sorted(logs, key=lambda x: x.get('timestamp', ''), reverse=True)[:3]
                log_lines = []
                for log in recent_logs:
                    action = log.get('action', 'inconnu')
                    user = f"<@{log.get('user_id')}>" if log.get('user_id') else "Système"
                    details = log.get('details', {})
                    url = details.get('url', '')[:30] if isinstance(details, dict) else ''
                    line = f"• `{action}` par {user}"
                    if url:
                        line += f" → `{url}…`"
                    log_lines.append(line)
                embed.add_field(name="📜 Derniers événements", value="\n".join(log_lines), inline=False)

            embed.set_footer(text="Données extraites de Supabase • Seiko Security")

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de la récupération des données : `{str(e)}`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
