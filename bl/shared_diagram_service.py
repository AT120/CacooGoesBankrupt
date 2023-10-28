import discord
from repository.repository import database
from consts import Reactions
import utils
from bl.cacoo_api import CacooException, cacoo

async def delete_diagram(
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