import discord
from repository.repository import database
from consts import Reactions
import utils
from bl.cacoo_api import CacooException, cacoo
import logging
import asyncio
from calendar import timegm
from paginator.DiagramsPaginator import DiagramsPaginator

async def delete_diagram_interactive(
    interaction: discord.Interaction,
    userId: int,
    diagramId: str
):
    if not await database.user_have_diagram(userId, diagramId):
        await interaction.response.send_message(
            Reactions.unauthorized + " Не похоже, что такая диаграмма была создана",
            ephemeral=True)
        return 
    
    await utils.ensure_defer(interaction, ephemeral=True)
    try:
        await cacoo.delete_diagram(diagramId)
        await database.delete_diagram(userId, diagramId)
    except CacooException as ex:
        await interaction.followup.send(Reactions.negative + " " + ex.user_message, ephemeral=True)
        return
    except:
        await interaction.followup.send(
            Reactions.negative + " Произошла непредвиденная ошибка", 
            ephemeral=True)
        raise

    await interaction.followup.send(Reactions.positive, ephemeral=True)


async def reload_whitelist(bot: discord.Client, database, whitelistServerId: int):
    await database.reset_white_list()
    guild = await bot.fetch_guild(whitelistServerId, with_counts=False)
    async for member in guild.fetch_members(limit=None):
        if (member.id != bot.user.id):
            await database.add_user_to_whitelist(member.id, member.name)
            
    logging.info("Whitelist have been reloaded")


async def reload_last_updated_time():
    diagramCount = await database.count_diagrams()
    diagramsProcessed = 0
    page = 0
    while diagramsProcessed < diagramCount:
        diagrams = await database.get_diagrams_page(page, 10) #TODO: установить нормальный
        new_times = await asyncio.gather(
            *[cacoo.diagram_last_use_time(dia.id) for dia in diagrams]
        )
        
        dbupdaters = []
        for i in range(len(diagrams)):
            await database.set_updatetime(diagrams[i].id, int(new_times[i].timestamp()))
            # dbupdaters.append(
            # )
        # await asyncio.gather(*dbupdaters)

        page += 1
        diagramsProcessed += len(diagrams)
        yield diagramsProcessed / diagramCount

async def list_diagrams(interaction: discord.Interaction, userId: int, search = ""):
    if len(search) == 0:
        search = None

    await utils.ensure_defer(interaction, ephemeral=True)

    pageSize = 10
    diagramsCount = await database.count_diagrams(userId, search)
    pag = DiagramsPaginator(userId, search, diagramsCount, pageSize, 60)
    await pag.display(interaction, suppress_embeds=True, ephemeral=True)