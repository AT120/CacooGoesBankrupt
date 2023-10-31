from aiohttp import web
from utils import get_application_dir
import discord_bot
from config import config

discord_bot.database.init(
    get_application_dir().joinpath(
        config.get("database-file")
    )
)
app = web.Application()
app.cleanup_ctx.append(discord_bot.cacoo.initialize)
app.on_startup.append(discord_bot.startup)

web.run_app(app)