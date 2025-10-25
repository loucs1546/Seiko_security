import discord
from discord.ext import commands
import config

class LogSetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="create-categorie-log", description="Crée une catégorie complète de salons de logs")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def create_log_category(self, interaction: discord.Interaction):
        guild = interaction.guild

        for category in guild.categories:
            if "log" in category.name.lower():
                await interaction.response.send_message(
                    f"❌ Une catégorie de logs existe déjà : **{category.name}**", 
                    ephemeral=True
                )
                return

        category = await guild.create_category(
            name="🔐・Logs Sécurité",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        names = ["📜・messages", "🎤・vocal", "🎫・tickets", "🛠️・commandes", "👑・rôles", "📛・profil", "🔗・liens", "🚨・menaces"]
        channels = {}
        for name in names:
            ch = await guild.create_text_channel(name=name, category=category)
            key = name.split("・")[1]
            if key == "messages": channels["messages"] = ch.id
            elif key == "vocal": channels["vocal"] = ch.id
            elif key == "tickets": channels["tickets"] = ch.id
            elif key == "commandes": channels["commands"] = ch.id
            elif key == "rôles": channels["roles"] = ch.id
            elif key == "profil": channels["profile"] = ch.id
            elif key == "liens": channels["links"] = ch.id
            elif key == "menaces": channels["threats"] = ch.id

        config.LOG_CHANNELS = channels
        await interaction.response.send_message(
            f"✅ Catégorie **{category.name}** créée avec {len(names)} salons !",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(LogSetupCog(bot))