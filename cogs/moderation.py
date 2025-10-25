import discord
from discord.ext import commands
import config

class ModerationCog(commands.Cog):
    @discord.app_commands.command(name="audit", description="Analyse la sécurité du serveur")
    async def audit(self, interaction: discord.Interaction):
        issues = []
        guild = interaction.guild
        if not guild.me.guild_permissions.administrator:
            issues.append("Bot sans permissions admin.")
        if any(role.permissions.administrator and not role.managed for role in guild.roles if role != guild.default_role):
            issues.append("Rôles admin non gérés.")
        score = max(0, 100 - len(issues) * 20)
        await interaction.response.send_message(
            f"🔍 **Audit**\nScore : {score}/100\nProblèmes : {', '.join(issues) or 'Aucun'}",
            ephemeral=True
        )

    @discord.app_commands.command(name="purge")
    @discord.app_commands.describe(limit="Nombre de messages à supprimer")
    async def purge(self, interaction: discord.Interaction, limit: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Permissions insuffisantes.", ephemeral=True)
            return
        deleted = await interaction.channel.purge(limit=limit)
        await interaction.response.send_message(f"🧹 {len(deleted)} messages supprimés.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ModerationCog())