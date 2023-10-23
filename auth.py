from discord.ext import commands
from repository.repository import database
from consts import Reactions

class Auth:
    def ADMIN(command):
        async def inner(ctx: commands.Context, *args):
            if ctx.author.id != 477114347496407040: #TODO: in config
                await ctx.message.add_reaction(Reactions.unauthorized)
                return 
            
            await command(ctx, *args)

        return inner

    def WHITELIST(command):
        async def inner(ctx: commands.Context, *args):
            if not await database.user_in_whitelist(ctx.author.id):
                await ctx.message.add_reaction(Reactions.unauthorized)
                return 
            
            await command(ctx, *args)

        return inner
