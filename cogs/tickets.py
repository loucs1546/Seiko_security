# cogs/tickets.py
import discord
from discord.ext import commands

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Définir la commande slash via bot.tree (pas via @commands.slash_command)
    @discord.app_commands.command(name="active", description="Active les webhooks pour les tickets")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def active(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Webhooks de tickets activés.", ephemeral=True)

    # Ajouter la commande à l'arbre quand le cog est chargé
    async def cog_load(self):
        self.bot.tree.add_command(self.active, guild=discord.Object(id=1289495334069862452))

    # Optionnel : retirer la commande à la décharge
    async def cog_unload(self):
        self.bot.tree.remove_command("active", guild=discord.Object(id=1289495334069862452))

# Fonction de setup pour le chargement du cog
async def setup(bot):
    await bot.add_cog(TicketCog(bot))
