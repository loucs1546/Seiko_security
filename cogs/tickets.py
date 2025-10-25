import discord
from discord.ext import commands

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[1289495334069862452])
    @commands.has_permissions(administrator=True)
    async def active(self, ctx):
        """Active les webhooks pour les tickets (à étendre)"""
        await ctx.respond("✅ Webhooks de tickets activés.", ephemeral=True)
        # Ici, tu pourras initialiser un webhook ou créer un salon de logs dédié

    # Tu pourras ajouter /rajout, /messageoff, etc. ici plus tard