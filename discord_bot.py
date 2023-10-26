import discord
from discord.ext import commands
from discord import app_commands
from typing import List
import cacoo_api
import keys
import logging
from repository.repository import database
import asyncio
import utils
from paginator.DiagramsPaginator import *
from auth import *
from consts import Reactions
from sync import lock_on_maintenance, performing_maintenance

logging.basicConfig(level=logging.INFO)
cacoo = cacoo_api.Cacoo(keys.get_cacoo_api_key())

_intents = discord.Intents.default()
_intents.members = True
# _intents.message_content = True
_client = commands.Bot(command_prefix=commands.when_mentioned, intents=_intents)
_tree = _client.tree
_whitelistServer = 1166037428906229840 #TODO: in config


##### events

@_client.event
async def on_ready():
    print(f"logged in as {_client.user}")
    await utils.reload_whitelist(_client, _whitelistServer)


@_client.event
async def on_member_join(member: discord.Member):
    await database.add_user_to_whitelist(member.id, member.name) #TODO: try/catch
    logging.info(f"user {member.name}/{member.id} was added to the whitelist")

@_client.event
async def on_member_remove(member: discord.Member):
    await database.remove_user_from_whitelist(member.id)
    logging.info(f"user {member.name}/{member.id} was removed from the whitelist")


##### ADMIN COMMANDS

@_client.command("reload_whitelist")
@AuthCommand.ADMIN
@performing_maintenance
async def _reload_whitelist(ctx: commands.Context):
    await utils.reload_whitelist(_client, _whitelistServer)
    await ctx.message.add_reaction(Reactions.positive)

@_client.command("test")
@AuthCommand.ADMIN
@performing_maintenance
async def _test_smth(ctx: commands.Context):
    await asyncio.sleep(10)


@_client.command("sync_commands") # TODO: hide in help
@AuthCommand.ADMIN
async def _sync_commands(ctx: commands.Context):
    try:
        await _tree.sync()
        await ctx.message.add_reaction(Reactions.positive)
    except Exception as ex:
        await asyncio.gather(
            ctx.message.add_reaction(Reactions.negative),
            ctx.author.send(ex)
        )

@_client.command("reset_cacoo_cache")
@AuthCommand.ADMIN
@performing_maintenance
async def _reset_cacoo_cache(ctx: commands.Context):
    await cacoo.reset_cache()
    await ctx.message.add_reaction(Reactions.positive)

    
@_client.command("stats")
@AuthCommand.ADMIN
async def _provide_stats(ctx: commands.Context):
    pass

###### USER COMMANDS

# @_tree.command(name="test_maintanence_lock")
# @lock_on_maintenance
# async def _test_lock(interaction: discord.Interaction):
#     await utils.defer_interaction(interaction)
#     await asyncio.sleep(5)
#     await interaction.followup.send(Reactions.working)



@_tree.command(name="new", description="создать новую диаграмму")
@app_commands.describe(title="название диаграммы")
@AuthSlash.WHITELIST
@lock_on_maintenance
async def _new_diagram(interaction: discord.Interaction, title: str = ""):
    await utils.defer_interaction(interaction, ephemeral=True)

    if len(title) == 0:
        title = "Untitled"
    try:
        diagramUrl = await cacoo.create_diagram(title)
        diagramId = utils.extract_id_from_url(diagramUrl)
        await database.store_new_diagram(interaction.user.id, diagramId, title)
    except cacoo_api.CacooException as ex:
        await interaction.followup.send(Reactions.negative + " " + ex.user_message, ephemeral=True)
        return
    except:
        await interaction.followup.send(
            Reactions.negative + " Произошла непредвиденная ошибка", 
            ephemeral=True)
        raise
    
    await asyncio.gather(
        interaction.user.send(diagramUrl),
        interaction.followup.send(Reactions.positive, ephemeral=True)
    )


@_tree.command(name="del", description="Удалить диаграмму")
@app_commands.describe(name="название диаграммы, которую нужно удалить")
@lock_on_maintenance
async def _delete_diagram(interaction: discord.Interaction, name: str):
    diagramId = name  # из автокомпплита вернется id 
    print("got delete command!", interaction.id)

    if not await database.user_have_diagram(interaction.user.id, diagramId):
        await interaction.response.send_message(
            Reactions.unauthorized + " Не похоже, что диаграмма с такой ссылкой была создана",  #TODO: не будет такого
            ephemeral=True)
        return 
    
    print("passed possesion check", interaction.id)
    
    await utils.defer_interaction(interaction, ephemeral=True)
    try:
        await cacoo.delete_diagram(diagramId)
        print("called api", interaction.id)
        await database.delete_diagram(diagramId)
        print("removed from database", interaction.id)
    except cacoo_api.CacooException as ex:
        await interaction.followup.send(Reactions.negative + " " + ex.user_message, ephemeral=True)
        return
    except:
        await interaction.followup.send(
            Reactions.negative + " Произошла непредвиденная ошибка", 
            ephemeral=True)
        raise

    await interaction.followup.send(Reactions.positive, ephemeral=True)
    print("response sended", interaction.id)
    print()


@_delete_diagram.autocomplete("name")
async def _remove_inline_autocomplete(
    interaction: discord.Interaction, 
    current: str, 
    # namespace: app_commands.Namespace
) -> List[app_commands.Choice[str]]:
    diagrams = await database.get_user_diagrams_page(
        interaction.user.id,
        0, 5, current
    )
    return [app_commands.Choice(name=dia.name, value=dia.id) for dia in diagrams]


@_tree.command(name="dia", description="Посмотреть список своих диаграмм")
@app_commands.describe(search="Поиск диаграмм по имени")
@lock_on_maintenance
async def _list_diagrams(interaction: discord.Interaction, search: str = ""):
    if len(search) == 0:
        search = None

    await utils.defer_interaction(interaction, ephemeral=True)

    pageSize = 10
    authorId = interaction.user.id 
    diagramsCount = await database.count_diagrams(authorId, search)
    loader = get_data_loader(authorId, pageSize, search)
    pag = DiagramsPaginator(loader, diagramsCount, pageSize, 30)
    await pag.display(interaction, suppress_embeds=True, ephemeral=True)


# @_tree.command(name="rem")
# @app_commands.describe()
# @lock_on_maintenance
# async def _remove_inline(interaction: discord.Interaction, search: str):
#     await interaction.response.send_message(f"about to delete {search}")




_discordApp = _client.start(keys.get_discord_token())
async def startup(app):
    await _discordApp

