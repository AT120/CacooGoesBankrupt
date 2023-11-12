from discord.ext import commands
import discord
from repository.repository import database
from consts import Reactions
from functools import wraps
from config import config


_admin_id = config.get("admin-discord-id")
class AuthCommand:
    def ADMIN(command):
        async def inner(ctx: commands.Context, *args):
            if ctx.author.id != _admin_id:
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

class AuthSlash:
    def ADMIN(command):
        @wraps(command)
        async def inner(interaction: discord.Interaction, *args, **kwargs):
            if interaction.user.id != _admin_id:
                await interaction.response.send_message(Reactions.unauthorized)
                return 
            
            await command(interaction, *args, **kwargs)

        return inner
    

    def WHITELIST(command):
        @wraps(command)
        async def inner(interaction: discord.Interaction, *args, **kwargs):
            if not await database.user_in_whitelist(interaction.user.id):
                await interaction.response.send_message(Reactions.unauthorized)
                return 
            
            await command(interaction, *args, **kwargs)

        return inner
    
    def ON_WHITELIST_SERVER(command):
        @wraps(command)
        async def inner(interaction: discord.Interaction, *args, **kwargs):
            if interaction.guild_id != config.get("whitelist-server-id"):
                await interaction.response.send_message(Reactions.unauthorized)
                return 
            
            await command(interaction, *args, **kwargs)

        return inner
