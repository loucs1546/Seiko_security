import discord
from discord.ext import commands
import config
from utils.db import ensure_guild_config
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")
    await ensure_guild_config(config.GUILD_ID)
    
    # Charger les cogs
    cog_paths = [
        "cogs.logging",
        "cogs.security.antiraid",
        "cogs.security.antispam",
        "cogs.security.link_filter",
        "cogs.moderation",
        "cogs.tickets",
        "cogs.logs_viewer"
    ]
    for cog in cog_paths:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog chargé : {cog}")
        except Exception as e:
            print(f"❌ Erreur : {cog} → {e}")
    
    guild = discord.Object(id=config.GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("🔁 Commandes slash synchronisées.")

bot.run(config.DISCORD_TOKEN)
