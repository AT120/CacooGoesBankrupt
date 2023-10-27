import discord
from discord.ext import commands
import cacoo_api
import keys
import logging
from repository.repository import database
import asyncio
import utils
from paginator.Paginator import Paginator
import paginator.DiagramsPaginator
from auth import AuthCommand
from consts import Reactions
from maintenance import lock_on_maintenance, performing_maintenance

logging.basicConfig(level=logging.INFO)
cacoo = cacoo_api.Cacoo(keys.get_cacoo_api_key())

_intents = discord.Intents.default()
_intents.members = True
_bot = commands.Bot(command_prefix=commands.when_mentioned, intents=_intents)
_whitelistServer = 1166037428906229840 #TODO: in config


##### events

@_bot.event
async def on_ready():
    print(f"logged in as {_bot.user}")


@_bot.event
async def on_member_join(member: discord.Member):
    await database.add_user_to_whitelist(member.id) #TODO: try/catch
    logging.info(f"user {member.name}/{member.id} was added to the whitelist")

@_bot.event
async def on_member_remove(member: discord.Member):
    await database.remove_user_from_whitelist(member.id)
    logging.info(f"user {member.name}/{member.id} was removed from the whitelist")


# @_bot.on_command_error
# async def 



##### ADMIN COMMANDS

@_bot.command("reload_whitelist")
@AuthCommand.ADMIN
@performing_maintenance
async def _reload_whitelist(ctx: commands.Context):
    await utils.reload_whitelist(_bot, _whitelistServer)
    await ctx.message.add_reaction(Reactions.positive)

@_bot.command("test")
@AuthCommand.ADMIN
@performing_maintenance
async def _test_smth(ctx: commands.Context):
    await asyncio.sleep(10)


@_bot.command("react")
@AuthCommand.ADMIN
@performing_maintenance
async def _test_react(ctx: commands.Context):
    await ctx.message.add_reaction(Reactions.positive)

@_bot.command("reset_cacoo_cache")
@AuthCommand.ADMIN
@performing_maintenance
async def _reset_cacoo_cache(ctx: commands.Context):
    await cacoo.reset_cache()
    await ctx.message.add_reaction(Reactions.positive)


@_bot.command("long")
@AuthCommand.ADMIN
async def _long_operation(ctx: commands.Context):
    await ctx.message.add_reaction(Reactions.working)
    await asyncio.sleep(20)
    await ctx.message.remove_reaction(Reactions.working, ctx.bot.user)

    


##### USER COMMANDS

@_bot.command("new")
@lock_on_maintenance
@AuthCommand.WHITELIST
async def _new_diagram(ctx: commands.Context, *args):
    title = " ".join(args)
    if len(title) == 0:
        title = "Untitled"
    try:
        diagramUrl = await cacoo.create_diagram(title)
        diagramId = utils.extract_id_from_url(diagramUrl)
        await database.store_new_diagram(ctx.author.id, diagramId, title)
    except: #TODO: cacoo error, differentiate between database exc and api exc
        await ctx.message.add_reaction(Reactions.negative)
        #TODO: error message
        return 
    
    await asyncio.gather(
        ctx.message.add_reaction(Reactions.positive),
        ctx.author.send(diagramUrl)
    )



@_bot.command("del")
@lock_on_maintenance
async def _delete_diagram(ctx: commands.Context, diagramUrl):
    diagramId = utils.extract_id_from_url(diagramUrl)
    if not await database.user_have_diagram(ctx.author.id, diagramId):
        await ctx.message.add_reaction(Reactions.unauthorized)
        return 
    
    try:
        await cacoo.delete_diagram(diagramUrl)
        await database.delete_diagram(diagramId)
    except: #TODO: cacoo error; differentiate between database exc and api exc
        await ctx.message.add_reaction(Reactions.negative)
        #TODO: error message
        return 

    await ctx.message.add_reaction(Reactions.positive)


@_bot.command("dia")
@lock_on_maintenance
async def _pagination_testing(ctx: commands.Context, *args):
    searchTerm = " ".join(args)
    if len(searchTerm) == 0:
        searchTerm = None

    pageSize = 10
    diagramsCount = await database.count_diagrams(ctx.author.id, searchTerm)
    loader = paginator.DiagramsPaginator.get_data_loader(ctx.author.id, pageSize, searchTerm)
    pag = Paginator(loader, ctx.author, diagramsCount, pageSize, 10)
    await pag.display(ctx.message)    


@_bot.command("mine")
async def _check_possesion(ctx: commands.Context, diagramUrl):
    pass


#TODO: event command_not_found


_discordApp = _bot.start(keys.get_discord_token())
async def startup(app):
    await _discordApp

