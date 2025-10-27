# cogs/config.py
import discord
from discord.ext import commands
import core_config as config

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="config", description="Configure le bot")
    async def config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        view = ConfigMainView(self.bot)
        await interaction.response.send_message("🔧 **Configuration du bot**", view=view, ephemeral=True)

class ConfigMainView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Sécurité", style=discord.ButtonStyle.primary)
    async def security_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🛡️ **Sécurité**", view=ConfigSecurityView(self.bot))

    @discord.ui.button(label="Logs", style=discord.ButtonStyle.secondary)
    async def logs_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="📜 **Logs**", view=ConfigLogsView(self.bot))

class ConfigSecurityView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Anti-Spam", style=discord.ButtonStyle.gray, custom_id="anti_spam")
    async def anti_spam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = config.CONFIG["security"]["anti_spam"]
        config.CONFIG["security"]["anti_spam"] = not current
        button.style = discord.ButtonStyle.green if not current else discord.ButtonStyle.gray
        button.label = "Anti-Spam ✅" if not current else "Anti-Spam"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Anti-Hack", style=discord.ButtonStyle.gray, custom_id="anti_hack")
    async def anti_hack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = config.CONFIG["security"]["anti_hack"]
        config.CONFIG["security"]["anti_hack"] = not current
        button.style = discord.ButtonStyle.green if not current else discord.ButtonStyle.gray
        button.label = "Anti-Hack ✅" if not current else "Anti-Hack"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Anti-Raid", style=discord.ButtonStyle.gray, custom_id="anti_raid")
    async def anti_raid_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        current = config.CONFIG["security"]["anti_raid"]
        config.CONFIG["security"]["anti_raid"] = not current
        button.style = discord.ButtonStyle.green if not current else discord.ButtonStyle.gray
        button.label = "Anti-Raid ✅" if not current else "Anti-Raid"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Retour", style=discord.ButtonStyle.danger)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="🔧 **Configuration du bot**", view=ConfigMainView(self.bot))

class ConfigLogsView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.button(label="Créer les salons", style=discord.ButtonStyle.success)
    async def create_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        for category in guild.categories:
            if "log" in category.name.lower() or "surveillance" in category.name.lower():
                await interaction.response.send_message(
                    f"❌ Une catégorie de logs existe déjà : **{category.name}**",
                    ephemeral=True
                )
                return

        try:
            category = await guild.create_category(
                name="🔐・Surveillance",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
            )

            mapping = [
                ("📜・messages", "messages"),
                ("🎤・vocal", "vocal"),
                ("🛠️・commandes", "commands"),
                ("👑・rôles", "roles"),
                ("📛・profil", "profile"),
                ("🔍・contenu", "content"),
                ("⚖️・sanctions", "sanctions")
            ]

            for name, key in mapping:
                ch = await guild.create_text_channel(name=name, category=category)
                config.CONFIG["logs"][key] = ch.id

            await interaction.response.send_message(
                f"✅ Catégorie **{category.name}** créée avec {len(mapping)} salons !",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {str(e)}", ephemeral=True)

    @discord.ui.button(label="Définir manuellement", style=discord.ButtonStyle.secondary)
    async def define_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "📝 Cliquez sur un type de log pour le configurer :",
            view=ConfigDefineTypeView(self.bot),
            ephemeral=True
        )

class ConfigDefineTypeView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

    @discord.ui.select(
        placeholder="Choisissez un type de log...",
        options=[
            discord.SelectOption(label="Messages", value="messages"),
            discord.SelectOption(label="Vocal", value="vocal"),
            discord.SelectOption(label="Commandes", value="commands"),
            discord.SelectOption(label="Rôles", value="roles"),
            discord.SelectOption(label="Profil", value="profile"),
            discord.SelectOption(label="Contenu", value="content"),
            discord.SelectOption(label="Sanctions", value="sanctions")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        log_type = select.values[0]
        await interaction.response.send_message(
            f"📌 Sélectionnez un salon pour les logs de **{log_type}** :",
            view=ConfigChannelSelectView(log_type),
            ephemeral=True
        )

class ConfigChannelSelectView(discord.ui.View):
    def __init__(self, log_type):
        super().__init__(timeout=300)
        self.log_type = log_type

    @discord.ui.channel_select(placeholder="Sélectionnez un salon texte...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = select.values[0]
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("❌ Veuillez choisir un salon texte.", ephemeral=True)
            return
        config.CONFIG["logs"][self.log_type] = channel.id
        await interaction.response.send_message(
            f"✅ Salon **{channel.mention}** défini pour **{self.log_type}**.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))