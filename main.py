# main.py
import discord
from discord.ext import commands
import core_config as config
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")
    
    cog_paths = [
        "cogs.logging",
        "cogs.security.antiraid",
        "cogs.security.antispam",
        "cogs.security.content_filter",
        "cogs.security.link_filter",
        "cogs.moderation_commands",  # ← Contient TOUTES les commandes
        "cogs.tickets",
        "cogs.config"
    ]
    
    for cog in cog_paths:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog chargé : {cog}")
        except Exception as e:
            print(f"❌ Erreur : {e}")

    # main.py — dans on_ready()
    await asyncio.sleep(1)
    guild = discord.Object(id=config.GUILD_ID)
    synced = await bot.tree.sync(guild=guild)  # ← PAS bot.tree.sync()
    print(f"✅ {len(synced)} commandes : {[c.name for c in synced]}")

bot.run(config.DISCORD_TOKEN)