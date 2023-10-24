import asyncio
from discord.ext import commands
from consts import Reactions
MAINTENANCE_LOCK = asyncio.Lock()
REQUESTS_IN_PROCESS = 0
MAINTENANCE_BEING_PERFORMED = False

def lock_on_maintenance(command):
    async def inner(ctx: commands.Context, *args):
        global REQUESTS_IN_PROCESS
        was_under_maintenance = False
        if MAINTENANCE_BEING_PERFORMED:
            try:
                await ctx.message.add_reaction(Reactions.working)
                was_under_maintenance = True
            except:
                pass

        await MAINTENANCE_LOCK.acquire()
        REQUESTS_IN_PROCESS += 1
        MAINTENANCE_LOCK.release()

        try:
            await command(ctx, *args)
        except:
            raise
        finally:
            REQUESTS_IN_PROCESS -= 1
            if was_under_maintenance:
                await ctx.message.remove_reaction(Reactions.working, ctx.bot.user)
  
    
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


