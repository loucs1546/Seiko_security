# utils/logging.py
import discord
import core_config as config

async def send_log_to(bot, log_type: str, embed: discord.Embed):
    channel_id = config.CONFIG["logs"].get(log_type)
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if channel:
        try:
            await channel.send(embed=embed)
        except Exception:
            pass