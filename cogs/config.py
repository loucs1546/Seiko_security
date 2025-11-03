import discord
from discord.ext import commands
from discord import app_commands
import core_config as config

class SecurityView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    @discord.ui.button(label="Anti-spam", style=discord.ButtonStyle.danger)
    async def antispam(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Simulation activation antispam
        await interaction.response.send_message("✅ Anti-spam activé", ephemeral=True)

    @discord.ui.button(label="Anti-hack", style=discord.ButtonStyle.danger)
    async def antihack(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Protection anti-hack activée", ephemeral=True)

    @discord.ui.button(label="Anti-raid", style=discord.ButtonStyle.danger)
    async def antiraid(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Mode anti-raid activé", ephemeral=True)

class ConfigView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=180)
        self.bot = bot

    @discord.ui.button(label="Cyber-sécurité", style=discord.ButtonStyle.primary)
    async def security(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ Configuration de la Sécurité",
            description="Choisissez les systèmes de protection à activer",
            color=discord.Color.red()
        )
        await interaction.response.send_message(
            embed=embed,
            view=SecurityView(self.bot),
            ephemeral=True
        )

    @discord.ui.button(label="Logs", style=discord.ButtonStyle.secondary)
    async def logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📋 Configuration des Logs",
            description="Utilisez les commandes suivantes:\n\n"
                       "`/logs messages` - Messages des utilisateurs\n"
                       "`/logs moderation` - Actions de modération\n"
                       "`/logs ticket` - Gestion des tickets\n"
                       "`/logs vocal` - Activité vocale\n"
                       "`/logs giveaway` - Suivi des giveaways\n"
                       "`/logs securite` - Alertes de sécurité",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="config", description="Configure le bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def config(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚙️ Configuration de Seiko",
            description="Choisissez une catégorie à configurer",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(
            embed=embed,
            view=ConfigView(self.bot),
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))
