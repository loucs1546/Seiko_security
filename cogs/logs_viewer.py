# cogs/logs_viewer.py
import discord
from discord.ext import commands
import config
from utils.db import supabase_select

class LogsViewerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.showdata_command = discord.app_commands.Command(
            name="showdata",
            description="Affiche les derniers logs de sécurité enregistrés",
            callback=self.showdata_callback
        )

    async def showdata_callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            logs = await supabase_select("logs", {"guild_id": str(config.GUILD_ID)})
            if not logs:
                await interaction.followup.send("📭 Aucun log trouvé dans la base de données.", ephemeral=True)
                return

            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            lines = []
            for log in logs[:25]:
                timestamp = log.get("timestamp", "")[:19].replace("T", " ")
                user_id = log.get("user_id")
                action = log.get("action", "inconnu")
                details = log.get("details", {})

                user_mention = f"<@{user_id}>" if user_id else "Système"
                detail_str = ""
                if isinstance(details, dict):
                    if "content" in details:
                        detail_str = f" « {details['content'][:50]}{'…' if len(details['content']) > 50 else ''} »"
                    elif "url" in details:
                        detail_str = f" [URL]"
                lines.append(f"**[{timestamp}]** {user_mention} → `{action}`{detail_str}")

            content = "\n".join(lines)
            if len(content) > 1900:
                content = content[:1900] + "\n…"
            await interaction.followup.send(f"📜 **Logs** ({len(logs)} total) :\n\n{content}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur : `{e}`", ephemeral=True)

    async def cog_load(self):
        guild = discord.Object(id=config.GUILD_ID)
        self.bot.tree.add_command(self.showdata_command, guild=guild)

    async def cog_unload(self):
        guild = discord.Object(id=config.GUILD_ID)
        self.bot.tree.remove_command("showdata", guild=guild)

async def setup(bot):
    await bot.add_cog(LogsViewerCog(bot))
