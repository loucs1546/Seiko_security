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
    print(f"✅ Connecté en tant que {bot.user}")
    
    # Charger les cogs
    for cog in ["cogs.logging", "cogs.tickets"]:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog chargé : {cog}")
        except Exception as e:
            print(f"❌ Erreur au chargement de {cog} : {e}")
    
    # Synchroniser les commandes slash (si tu en as)
    guild = discord.Object(id=config.GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("🔁 Commandes slash synchronisées.")

bot.run(config.DISCORD_TOKEN)
