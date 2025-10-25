# main.py
import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=config.GUILD_ID)
    print(f"✅ Connecté en tant que {bot.user}")
    
    # Charger les cogs
    await bot.load_extension("cogs.tickets")
    await bot.load_extension("cogs.logging")
    
    # Synchroniser les commandes slash POUR CET SERVEUR UNIQUEMENT
    await bot.tree.sync(guild=guild)
    print("🔁 Commandes slash synchronisées pour le serveur cible.")

bot.run(config.DISCORD_TOKEN)
