import discord
import logging
import time
from functools import wraps

def extract_id_from_url(diagramUrl: str) -> str:
    urlParts = diagramUrl.split("/")
    if diagramUrl.startswith("http"):
        return urlParts[4] if len(urlParts) > 4 else "0" 
    else:
        return urlParts[2] if len(urlParts) > 2 else "0"

def make_url_from_id(diagramId: str) -> str:
    return f"https://cacoo.com/diagrams/{diagramId}"


async def reload_whitelist(bot: discord.Client, database, whitelistServerId: int):
    await database.reset_white_list()
    guild = await bot.fetch_guild(whitelistServerId, with_counts=False)
    async for member in guild.fetch_members(limit=None):
        if (member.id != bot.user.id):
            await database.add_user_to_whitelist(member.id, member.name)
            
    logging.info("Whitelist have been reloaded")

async def defer_interaction(interaction: discord.Interaction, **kwargs):
    if not interaction.response.is_done():
        await interaction.response.defer(**kwargs)


def format_time(timestamp: int) -> str:
    datetime = time.localtime(timestamp)
    return time.strftime("%d/%m/%y %H:%M", datetime)



def timeit(command):
    @wraps(command)
    async def inner(*args, **kwargs):
        startTime = time.time()
        res = await command(*args, **kwargs)
        logging.info(f"{args[0].id} - {(time.time()-startTime)*1000}ms")
        return res

    return inner


