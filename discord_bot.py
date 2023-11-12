import discord
import logging, asyncio, utils
from discord.ext import commands
from discord import app_commands
from typing import List
from bl.cacoo_api import cacoo, CacooException
from bl.shared_diagram_logic import *
from repository.repository import database
from paginator.DiagramsPaginator import DiagramsPaginator
from paginator.StatsPaginator import StatsPaginator
from paginator.UnusedDiagramsPaginator import UnusedDiagramsPaginator
from decorators.auth import *
from consts import Reactions
from decorators.maintenance import lock_on_maintenance, performing_maintenance
from time import time
from config import config


_intents = discord.Intents.default()
_intents.members = True
_client = commands.Bot(command_prefix=commands.when_mentioned, intents=_intents, help_command=None)
_tree = _client.tree
_whitelistServer = config.get("whitelist-server-id")


##### events

@_client.event
async def on_ready():
    logging.info(f"logged in as {_client.user}")
    await reload_whitelist(_client, database, _whitelistServer)


@_client.event
async def on_member_join(member: discord.Member):
    await database.add_user_to_whitelist(member.id, member.name) #TODO: try/catch
    logging.info(f"user {member.name}/{member.id} was added to the whitelist")

@_client.event
async def on_member_remove(member: discord.Member):
    await database.remove_user_from_whitelist(member.id)
    logging.info(f"user {member.name}/{member.id} was removed from the whitelist")


##### ADMIN COMMANDS

@_client.command("get_guilds")
@AuthCommand.ADMIN
async def _get_guilds(ctx: commands.Context):
    msg = ""
    for guild in _client.guilds:
        msg += f"{guild.id}/{guild.name}\n"

    await ctx.author.send(msg)

@_client.command("reload_whitelist")
@AuthCommand.ADMIN
@performing_maintenance
async def _reload_whitelist(ctx: commands.Context):
    await reload_whitelist(_client, database, _whitelistServer) #TODO: try catch
    await ctx.message.add_reaction(Reactions.positive)


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
    await cacoo.reset_cache() #TODO: try catch
    await ctx.message.add_reaction(Reactions.positive)



##### ADMIN SLAHSES

@_tree.command(name="userstats", description="статистика использования бота")
@app_commands.guild_only()
@app_commands.describe(time_span="временной промежуток для показа статистики")
@app_commands.choices(time_span=[
    app_commands.Choice(name="за последние 7 дней", value=0),
    app_commands.Choice(name="за последние 30 дней", value=1),
    app_commands.Choice(name="за все время", value=2),
])
@AuthSlash.ON_WHITELIST_SERVER
async def _provide_stats(interaction: discord.Interaction, time_span: app_commands.Choice[int]):
    after = 0
    match time_span.value:
        case 0:
            after = int(time() - 604800) 
        case 1:
            after = int(time() - 2592000)
        case 2:
            after = None

    diagramsCount, userCount, _ = await asyncio.gather(
        database.count_diagrams(after=after),
        database.count_users(after),
        utils.ensure_defer(interaction, ephemeral=True)
    )
    
    pag = StatsPaginator(
        _client, after, userCount, 10, 60,
        f"{time_span.name} было создано диаграмм: {diagramsCount}\n\n"
    )
    await pag.display(interaction)


@_tree.command(name="unusedstats", description="неиспользуемые диаграммы")
@app_commands.guild_only()
@lock_on_maintenance
@AuthSlash.ON_WHITELIST_SERVER
async def _unused_diagrams(interaction: discord.Interaction):
    #TODO: РАСКОМЕНТИРАСКОМЕНТИРАСКОМЕНТИ
    # msg = "Загружаю информацию о использовании с Cacoo... "
    # await interaction.response.send_message(msg + utils.load_bar(0), ephemeral=True)

    # async for progress in reload_last_updated_time():
    #     await interaction.edit_original_response(content=msg + utils.load_bar(progress))

    await utils.ensure_defer(interaction, ephemeral=True)
    count = await database.count_diagrams()
    pag = UnusedDiagramsPaginator(_client, count)
    await pag.display(interaction)


@_tree.command(name="admindel", description="удалить чужую диаграмму")
@app_commands.guild_only()
@app_commands.describe(user='логин пользователя в Discord (добавьте "/2" в конце запроса, чтобы посмотреть другие варианты)')
@app_commands.describe(diagram='диаграмма, которую нужно удалить (добавьте "/2" в конце запроса, чтобы посмотреть другие варианты)')
@AuthSlash.ON_WHITELIST_SERVER
@lock_on_maintenance
async def _delete_any_diagram(
    interaction: discord.Interaction,
    user: str,
    diagram: str
):
    await delete_diagram_interactive(interaction, int(user), diagram)

@_delete_any_diagram.autocomplete("user")
async def _delete_other_user_autocomplete(
    interaction: discord.Interaction, 
    current: str, 
) -> List[app_commands.Choice[str]]:
    searchTerm, page = utils.split_term_page(current)
    res = await database.search_users(page, 7, searchTerm)
    return [app_commands.Choice(name=i[1], value=str(i[0])) for i in res]

@_delete_any_diagram.autocomplete("diagram")
async def _delete_other_diagram_autocomplete(
    interaction: discord.Interaction, 
    current: str, 
) -> List[app_commands.Choice[str]]:
    searchTerm, page = utils.split_term_page(current)
    userId = int(interaction.namespace.user)
    diagrams = await database.get_diagrams_page(page, 7, userId, searchTerm)
    return [app_commands.Choice(name=dia.name_with_time()[:100], value=dia.id) for dia in diagrams]


@_tree.command(name="admindia", description="Посмотреть список диаграмм других пользователей")
@app_commands.guild_only()
@app_commands.describe(user='пользователь, чьи диаграммы посмотреть (добавьте "/2" в конце запроса, чтобы посмотреть другие варианты)')
@AuthSlash.WHITELIST
async def _dia_other(interaction: discord.Interaction, user: str):
    userId = int(user)
    await list_diagrams(interaction, userId)

@_dia_other.autocomplete("user")
async def _dia_other_user_autocomplete(
    interaction: discord.Interaction, 
    current: str, 
) -> List[app_commands.Choice[str]]:
    searchTerm, page = utils.split_term_page(current) #TODO: написать пояснения про пагинацию
    res = await database.search_users(page, 7, searchTerm)
    return [app_commands.Choice(name=i[1], value=str(i[0])) for i in res]



###### USER COMMANDS

@_tree.command(name="new", description="создать новую диаграмму")
@app_commands.describe(title="название диаграммы")
@AuthSlash.WHITELIST
@lock_on_maintenance
async def _new_diagram(interaction: discord.Interaction, title: str = ""):
    await utils.ensure_defer(interaction, ephemeral=True)

    if len(title) == 0:
        title = "Untitled"
    try:
        diagramUrl = await cacoo.create_diagram(title)
        diagramId = utils.extract_id_from_url(diagramUrl)
        await database.store_new_diagram(interaction.user.id, diagramId, title)
    except CacooException as ex:
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
@app_commands.describe(name='название диаграммы, которую нужно удалить (добавьте "/2" в конце запроса, чтобы посмотреть другие варианты)')
@lock_on_maintenance
async def _delete_diagram(interaction: discord.Interaction, name: str):
    diagramId = name  # из автокомпплита вернется id 
    await delete_diagram_interactive(interaction, interaction.user.id, diagramId)


@_delete_diagram.autocomplete("name")
async def _delete_inline_autocomplete(
    interaction: discord.Interaction, 
    current: str, 
    # namespace: app_commands.Namespace
) -> List[app_commands.Choice[str]]:
    searchTerm, page = utils.split_term_page(current)
    diagrams = await database.get_diagrams_page(page, 7, interaction.user.id, searchTerm)
    return [app_commands.Choice(name=dia.name_with_time()[:100], value=dia.id) for dia in diagrams]


@_tree.command(name="dia", description="Посмотреть список своих диаграмм")
@app_commands.describe(search="Поиск диаграмм по имени")
@lock_on_maintenance
async def _list_diagrams(interaction: discord.Interaction, search: str = ""):
    await list_diagrams(interaction, interaction.user.id, search)




_discordApp = _client.start(config.get("discord-token"))
async def startup(app):
    await _discordApp

