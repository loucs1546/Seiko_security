# cogs/logs_viewer.py
import discord
from discord.ext import commands
import config
from utils.db import supabase_select

class LogsViewerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="showdata", description="Affiche les derniers logs de sécurité enregistrés")
    async def showdata(self, interaction: discord.Interaction):
        # 🔒 Réservé aux administrateurs
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Vous n'avez pas la permission d'utiliser cette commande.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)  # Évite le timeout

        try:
            # Récupère les logs du serveur, triés par timestamp (les plus récents en premier)
            logs = await supabase_select("logs", {"guild_id": str(config.GUILD_ID)})
            
            if not logs:
                await interaction.followup.send("📭 Aucun log trouvé dans la base de données.", ephemeral=True)
                return

            # Trie par timestamp décroissant (plus récent en premier)
            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            recent_logs = logs[:25]  # Discord limite la taille du message

            # Construire le contenu du message
            lines = []
            for log in recent_logs:
                timestamp = log.get("timestamp", "")[:19].replace("T", " ")  # Format lisible
                user_id = log.get("user_id")
                target_id = log.get("target_id")
                action = log.get("action", "inconnu")
                details = log.get("details", {})

                user_mention = f"<@{user_id}>" if user_id else "Système"
                target_mention = f" → <@{target_id}>" if target_id else ""

                # Extraire un résumé des détails
                detail_str = ""
                if isinstance(details, dict):
                    if "content" in details:
                        detail_str = f" « {details['content'][:50]}{'…' if len(details['content']) > 50 else ''} »"
                    elif "url" in details:
                        detail_str = f" [URL : {details['url'][:40]}{'…' if len(details['url']) > 40 else ''}]"
                    elif "join_count" in details:
                        detail_str = f" ({details['join_count']} membres en 10s)"

                line = f"**[{timestamp}]** {user_mention}{target_mention} → `{action}`{detail_str}"
                lines.append(line)

            # Créer un embed ou un message texte (meilleur pour beaucoup de lignes)
            content = "\n".join(lines)
            if len(content) > 1900:
                content = content[:1900] + "\n… (tronqué)"

            await interaction.followup.send(
                f"📜 **Derniers logs de sécurité** (total : {len(logs)}) :\n\n{content}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.followup.send(
                f"❌ Erreur lors de la récupération des logs : `{str(e)}`",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(LogsViewerCog(bot))
