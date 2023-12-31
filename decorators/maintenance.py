import asyncio
from discord.ext import commands
from consts import Reactions
from functools import wraps

MAINTENANCE_LOCK = asyncio.Lock()
REQUESTS_IN_PROCESS = 0
MAINTENANCE_BEING_PERFORMED = False

async def empty(*args, **kwargs):
    pass

def lock_on_maintenance(command):
    @wraps(command)
    async def inner(*args, **kwargs):
        global REQUESTS_IN_PROCESS

        await MAINTENANCE_LOCK.acquire()
        REQUESTS_IN_PROCESS += 1
        MAINTENANCE_LOCK.release()

        try:
            await command(*args, **kwargs)
        except:
            raise
        finally:
            REQUESTS_IN_PROCESS -= 1
  
    
    return inner



def performing_maintenance(command):
    async def inner(ctx: commands.Context, *args):
        global MAINTENANCE_BEING_PERFORMED
        await ctx.message.add_reaction(Reactions.working)
        await MAINTENANCE_LOCK.acquire()
        MAINTENANCE_BEING_PERFORMED = True
        while REQUESTS_IN_PROCESS != 0:
            await asyncio.sleep(0.5)


        await command(ctx, *args),
        await ctx.message.remove_reaction(Reactions.working, ctx.bot.user)

        MAINTENANCE_BEING_PERFORMED = False
        MAINTENANCE_LOCK.release() 
    return inner


