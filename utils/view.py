# utils/views.py
import discord
from discord.ui import View, Button

class ContentReviewView(View):
    def __init__(self, message_content: str, author: discord.Member, original_channel: discord.TextChannel):
        super().__init__(timeout=600)  # 10 minutes
        self.message_content = message_content
        self.author = author
        self.original_channel = original_channel

    @discord.ui.button(label="✅ Valider", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Renvoyer le message dans le salon d'origine
        await self.original_channel.send(f"{self.author.mention} (message validé par modérateur)\n{self.message_content}")
        await interaction.response.edit_message(content="✅ Message restauré.", view=None)

    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Message supprimé définitivement.", view=None)