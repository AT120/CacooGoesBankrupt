from aiohttp import web
from utils import get_application_dir, setup_logging
import discord_bot
from config import config

setup_logging(config.get("log-level"))

discord_bot.database.init_connection(
    get_application_dir().joinpath(
        config.get("database-file")
    )
)


app = web.Application()
app.cleanup_ctx.append(discord_bot.cacoo.initialize)
app.on_startup.append(discord_bot.startup)

web.run_app(app)