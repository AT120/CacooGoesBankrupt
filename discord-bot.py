import discord
# from discord.ext import 
import cacoo_api
import aiohttp
from aiohttp import web
intents = discord.Intents.default()
client = discord.Client(intents=intents)
cacoo = cacoo_api.Cacoo("", client.loop)
# cacoo = cacoo_api.Cacoo()

@client.event
async def on_ready():
    print(f"logged in as {client.user}")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    
    # await message.channel.send(f"Здоровеньки булы {message.author.display_name}!")
    await message.author.send(f"ща попробую, сек")
    key = await cacoo.get_organization_key()
    await message.author.send(f"Ты че мне пишешь, э, я твой организация знаю {key}?")



discordApp = client.start("")
async def startup(app):
    await discordApp

# app.on_startup.append

app = web.Application(debug=True)
app.cleanup_ctx.append(cacoo.create_session)
app.on_startup.append(startup)

web.run_app(app)



# web.run_app(app)
