import discord
from repository.repository import database


def extract_id_from_url(diagramUrl: str) -> str:
    if diagramUrl.startswith("http"):
        return diagramUrl.split("/")[4]
    else:
        return diagramUrl.split("/")[2]

def make_url_from_id(diagramId: str) -> str:
    return f"https://cacoo.com/diagrams/{diagramId}"


async def reload_whitelist(bot: discord.Client, whitelistServerId: int):
    await database.reset_white_list()
    guild = await bot.fetch_guild(whitelistServerId, with_counts=False)
    async for member in guild.fetch_members(limit=None):
        if (member.id != bot.user.id):
            await database.add_user_to_whitelist(member.id)
        