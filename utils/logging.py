# utils/logging.py
import asyncio
import discord
import core_config as config

async def send_log_to(bot, log_type: str, content):
    channel_id = config.CONFIG.get("logs", {}).get(log_type)
    if not channel_id:
        return False
    channel = bot.get_channel(channel_id)
    if not channel:
        return False
    try:
        if isinstance(content, discord.Embed):
            await channel.send(embed=content)
        else:
            await channel.send(content)
        return True
    except:
        return False