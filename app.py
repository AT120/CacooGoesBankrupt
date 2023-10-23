from aiohttp import web
import cacoo_api
import discord_bot

discord_bot.database.init("database.db") #TODO: in config
app = web.Application()
app.cleanup_ctx.append(discord_bot.cacoo.initialize)
app.on_startup.append(discord_bot.startup)

web.run_app(app)