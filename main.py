import discord
from discord.ext import commands
import config
from cogs import logging, tickets

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    guild = bot.get_guild(config.GUILD_ID)
    if guild:
        print(f"✅ Connecté à {guild.name} (ID: {guild.id})")
        print(f"🤖 Seiko est prêt !")
    else:
        print("❌ Le bot n'est pas dans le serveur cible.")

    # Charger les modules
    await bot.add_cog(logging.LoggingCog(bot))
    await bot.add_cog(tickets.TicketCog(bot))

bot.run(config.DISCORD_TOKEN)
