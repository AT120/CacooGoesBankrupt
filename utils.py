import discord
from repository.repository import database
import logging

def extract_id_from_url(diagramUrl: str) -> str:
    urlParts = diagramUrl.split("/")
    if diagramUrl.startswith("http"):
        return urlParts[4] if len(urlParts) > 4 else "0" 
    else:
        return urlParts[2] if len(urlParts) > 2 else "0"

def make_url_from_id(diagramId: str) -> str:
    return f"https://cacoo.com/diagrams/{diagramId}"


async def reload_whitelist(bot: discord.Client, whitelistServerId: int):
    await database.reset_white_list()
    guild = await bot.fetch_guild(whitelistServerId, with_counts=False)
    async for member in guild.fetch_members(limit=None):
        if (member.id != bot.user.id):
            await database.add_user_to_whitelist(member.id, member.name)
            
    logging.info("Whitelist have been reloaded")

async def defer_interaction(interaction: discord.Interaction, **kwargs):
    if not interaction.response.is_done():
        await interaction.response.defer(**kwargs)