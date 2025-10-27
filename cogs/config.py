# cogs/config.py
import discord
from discord.ext import commands
import core_config as config

class ConfigCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="config", description="Interface de configuration avancée")
    async def config(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Réservé aux administrateurs.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔧 Configuration de CyberWatch",
            description="Choisissez une section à configurer :",
            color=0x3498db
        )
        view = MainConfigView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class MainConfigView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=600)
        self.bot = bot

    @discord.ui.button(label="🛡️ Sécurité", style=discord.ButtonStyle.primary)
    async def security(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = SecurityConfigView.get_embed()
        await interaction.response.edit_message(embed=embed, view=SecurityConfigView(self.bot))

    @discord.ui.button(label="📜 Logs", style=discord.ButtonStyle.secondary)
    async def logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📜 Configuration des Logs",
            description="Choisissez une option :",
            color=0x2ecc71
        )
        view = LogsConfigView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

class SecurityConfigView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=600)
        self.bot = bot

    @staticmethod
    def get_embed():
        s = config.CONFIG["security"]
        status = lambda x: "✅ **Activé**" if x else "❌ **Désactivé**"
        embed = discord.Embed(
            title="🛡️ Sécurité",
            description="Cliquez pour basculer l'état.",
            color=0xe74c3c
        )
        embed.add_field(name="🤖 Anti-Spam", value=status(s["anti_spam"]), inline=False)
        embed.add_field(name="👥 Anti-Raid", value=status(s["anti_raid"]), inline=False)
        embed.add_field(name="🕵️ Anti-Hack", value=status(s["anti_hack"]), inline=False)
        return embed

    async def toggle(self, interaction: discord.Interaction, key: str):
        current = config.CONFIG["security"][key]
        config.CONFIG["security"][key] = not current
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Anti-Spam", emoji="🤖", style=discord.ButtonStyle.secondary)
    async def btn_spam(self, interaction, button):
        await self.toggle(interaction, "anti_spam")

    @discord.ui.button(label="Anti-Raid", emoji="👥", style=discord.ButtonStyle.secondary)
    async def btn_raid(self, interaction, button):
        await self.toggle(interaction, "anti_raid")

    @discord.ui.button(label="Anti-Hack", emoji="🕵️", style=discord.ButtonStyle.secondary)
    async def btn_hack(self, interaction, button):
        await self.toggle(interaction, "anti_hack")

    @discord.ui.button(label="⬅️ Retour", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button):
        embed = discord.Embed(
            title="🔧 Configuration de CyberWatch",
            description="Choisissez une section :",
            color=0x3498db
        )
        await interaction.response.edit_message(embed=embed, view=MainConfigView(self.bot))

class LogsConfigView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=600)
        self.bot = bot

    @discord.ui.button(label="🆕 Créer les salons", style=discord.ButtonStyle.success)
    async def create_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        for cat in guild.categories:
            if "log" in cat.name.lower() or "surveillance" in cat.name.lower():
                await interaction.response.send_message(f"❌ Catégorie existante : **{cat.name}**", ephemeral=True)
                return

        try:
            cat = await guild.create_category(
                name="🔐・Surveillance",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
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
                ch = await guild.create_text_channel(name=name, category=cat)
                config.CONFIG["logs"][key] = ch.id
            await interaction.response.send_message(f"✅ {len(mapping)} salons créés dans **{cat.name}**.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)

    @discord.ui.button(label="⬅️ Retour", style=discord.ButtonStyle.danger)
    async def back(self, interaction, button):
        embed = discord.Embed(
            title="🔧 Configuration de CyberWatch",
            description="Choisissez une section :",
            color=0x3498db
        )
        await interaction.response.edit_message(embed=embed, view=MainConfigView(self.bot))

async def setup(bot):
    await bot.add_cog(ConfigCog(bot))