import discord
from discord.ext import commands
from discord import app_commands
import core_config as config

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="prefix", description="Change le préfixe du bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def change_prefix(self, interaction: discord.Interaction, nouveau_prefix: str):
        # Note: comme on utilise slash commands principalement, 
        # ceci est plus pour la compatibilité
        self.bot.command_prefix = nouveau_prefix
        await interaction.response.send_message(
            f"✅ Préfixe changé pour `{nouveau_prefix}`", 
            ephemeral=True
        )

    @app_commands.command(name="config-status", description="Affiche la configuration actuelle")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_config(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📝 Configuration actuelle",
            color=discord.Color.blue()
        )
        
        # Afficher les salons de logs configurés
        logs_config = config.CONFIG.get("logs", {})
        logs_txt = "\n".join(
            f"• **{log_type}**: <#{channel_id}>" 
            for log_type, channel_id in logs_config.items()
        ) or "Aucun salon configuré"
        
        embed.add_field(
            name="📋 Salons de logs",
            value=logs_txt,
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))
