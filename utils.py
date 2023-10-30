import discord
import logging
import time
from functools import wraps
from math import ceil

def extract_id_from_url(diagramUrl: str) -> str:
    urlParts = diagramUrl.split("/")
    if diagramUrl.startswith("http"):
        return urlParts[4] if len(urlParts) > 4 else "0" 
    else:
        return urlParts[2] if len(urlParts) > 2 else "0"

def make_url_from_id(diagramId: str) -> str:
    return f"https://cacoo.com/diagrams/{diagramId}"


async def ensure_defer(interaction: discord.Interaction, **kwargs):
    if not interaction.response.is_done():
        await interaction.response.defer(**kwargs)


def format_time(timestamp: int) -> str:
    datetime = time.localtime(timestamp)
    return time.strftime("%d/%m/%y %H:%M", datetime)


def days_since(timestamp: int) -> int:
    return int((time.time() - timestamp) / 86400)


def timeit(command):
    @wraps(command)
    async def inner(*args, **kwargs):
        startTime = time.time()
        res = await command(*args, **kwargs)
        # logging.info(f"{args[0].id} - {(time.time()-startTime)*1000}ms")
        logging.info(f"{(time.time()-startTime)*1000}ms")
        return res

    return inner


def split_term_page(query: str):
    sepIdx = query.rfind("/")
    if (sepIdx == -1):
        return query, 0
    term, page = query[:sepIdx], query[sepIdx+1:]
    try:
        page = int(page)
    except:
        return term, 0
    page -= 1
    page = 0 if page < 0 else page
    return term, page 


def load_bar(progress: float) -> str:
    LEN = 20
    done = int(progress * LEN)
    working = LEN - done
    return "```/" + "#" * done + "-" * working + "/```"

