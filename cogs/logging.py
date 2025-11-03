# cogs/logging.py
import discord
from discord.ext import commands
import core_config as config
from datetime import datetime

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log_to_channel(self, log_type: str, embed: discord.Embed):
        if not isinstance(config.CONFIG, dict) or "logs" not in config.CONFIG:
            return
        channel_id = config.CONFIG["logs"].get(log_type)
        if channel_id:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        embed = discord.Embed(
            title="💬 Message envoyé",
            description=f"**Auteur:** {message.author.mention}\n**Salon:** {message.channel.mention}\n**Contenu:** {message.content}",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        await self.log_to_channel("messages", embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=f"**Auteur:** {message.author.mention}\n**Salon:** {message.channel.mention}\n**Contenu:** {message.content}",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        await self.log_to_channel("messages", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot: return
        if before.content == after.content: return
        embed = discord.Embed(
            title="✏️ Message modifié",
            description=f"**Auteur:** {before.author.mention}\n**Salon:** {before.channel.mention}",
            color=0xffa500,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Avant", value=before.content, inline=False)
        embed.add_field(name="Après", value=after.content, inline=False)
        await self.log_to_channel("messages", embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel: return
        
        embed = discord.Embed(
            title="🎤 Activité vocale",
            description=f"**Membre:** {member.mention}",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        if after.channel:
            embed.add_field(name="Action", value=f"A rejoint {after.channel.name}")
        else:
            embed.add_field(name="Action", value=f"A quitté {before.channel.name}")
            
        await self.log_to_channel("vocal", embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(
                title="👤 Pseudo modifié",
                description=f"**Membre:** {before.mention}",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Avant", value=before.nick or before.name)
            embed.add_field(name="Après", value=after.nick or after.name)
            await self.log_to_channel("moderation", embed)

    @discord.app_commands.command(name="logs-messages")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def logs_messages(self, interaction: discord.Interaction, salon: discord.TextChannel):
        """Configure le salon pour les logs de messages"""
        config.CONFIG.setdefault("logs", {})["messages"] = salon.id
        await interaction.response.send_message(f"✅ Les logs de messages seront envoyés dans {salon.mention}", ephemeral=True)

    @discord.app_commands.command(name="logs-moderation")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def logs_moderation(self, interaction: discord.Interaction, salon: discord.TextChannel):
        """Configure le salon pour les logs de modération"""
        config.CONFIG.setdefault("logs", {})["moderation"] = salon.id
        await interaction.response.send_message(f"✅ Les logs de modération seront envoyés dans {salon.mention}", ephemeral=True)

    @discord.app_commands.command(name="logs-vocal")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def logs_vocal(self, interaction: discord.Interaction, salon: discord.TextChannel):
        """Configure le salon pour les logs vocaux"""
        config.CONFIG.setdefault("logs", {})["vocal"] = salon.id
        await interaction.response.send_message(f"✅ Les logs vocaux seront envoyés dans {salon.mention}", ephemeral=True)

    @discord.app_commands.command(name="logs-securite")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def logs_securite(self, interaction: discord.Interaction, salon: discord.TextChannel):
        """Configure le salon pour les logs de sécurité"""
        config.CONFIG.setdefault("logs", {})["securite"] = salon.id
        await interaction.response.send_message(f"✅ Les logs de sécurité seront envoyés dans {salon.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))