import discord
from discord.ext import commands
from discord import app_commands
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


@_client.event
async def on_member_join(member: discord.Member):
    await database.add_user_to_whitelist(member.id) #TODO: try/catch
    logging.info(f"user {member.name}/{member.id} was added to the whitelist")

@_client.event
async def on_member_remove(member: discord.Member):
    await database.remove_user_from_whitelist(member.id)
    logging.info(f"user {member.name}/{member.id} was removed from the whitelist")


# @_bot.on_command_error
# async def 



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


# @_bot.command("react")
# @Auth.ADMIN
# @performing_maintenance
# async def _test_react(ctx: commands.Context):
#     await ctx.message.add_reaction(Reactions.positive)

@_client.command("reset_cacoo_cache")
@AuthCommand.ADMIN
@performing_maintenance
async def _reset_cacoo_cache(ctx: commands.Context):
    await cacoo.reset_cache()
    await ctx.message.add_reaction(Reactions.positive)


@_client.command("long")
@AuthCommand.ADMIN
async def _long_operation(ctx: commands.Context):
    await ctx.message.add_reaction(Reactions.working)
    await asyncio.sleep(20)
    await ctx.message.remove_reaction(Reactions.working, ctx.bot.user)

    


# ##### USER COMMANDS


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
    except: #TODO: cacoo error, differentiate between database exc and api exc
        await interaction.followup.send(Reactions.negative, ephemeral=True)
        #TODO: error message
        return 
    
    await asyncio.gather(
        interaction.user.send(diagramUrl),
        interaction.followup.send(Reactions.positive, ephemeral=True)
    )

    1
@_tree.command(name="del", description="Удалить диаграмму")
@app_commands.describe(diagram_url="ссылка на диаграмму, которую нужно удалить")
@lock_on_maintenance
async def _delete_diagram(interaction: discord.Interaction, diagram_url: str):
    diagramId = utils.extract_id_from_url(diagram_url)
    if not await database.user_have_diagram(interaction.user.id, diagramId):
        await interaction.response.send_message(Reactions.unauthorized, ephemeral=True)
        return 
    
    await utils.defer_interaction(interaction, ephemeral=True)
    try:
        await cacoo.delete_diagram(diagram_url)
        await database.delete_diagram(diagramId)
    except: #TODO: cacoo error; differentiate between database exc and api exc
        await interaction.followup.send(Reactions.negative, ephemeral=True)
        #TODO: error message
        return 

    await interaction.followup.send(Reactions.positive, ephemeral=True)


@_tree.command(name="dia", description="Посмотреть список своих диаграмм")
@app_commands.describe(search="Поиск диаграмм по имени")
@lock_on_maintenance
async def _pagination_testing(interaction: discord.Interaction, search: str = ""):
    if len(search) == 0:
        search = None

    await utils.defer_interaction(interaction, ephemeral=True)

    pageSize = 10
    authorId = interaction.user.id 
    diagramsCount = await database.count_diagrams(authorId, search)
    loader = get_data_loader(authorId, pageSize, search)
    pag = DiagramsPaginator(loader, diagramsCount, pageSize, 10)
    await pag.display(interaction, suppress_embeds=True, ephemeral=True)


_discordApp = _client.start(keys.get_discord_token())
async def startup(app):
    await _discordApp

