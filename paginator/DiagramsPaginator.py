from repository.repository import database
import utils
from paginator.Paginator import Paginator
import discord

def get_data_loader(userId: int, pageSize: int, searchTerm: str | None):
    async def load_data(page):
        diagrams = await database.get_user_diagrams_page(userId, page, pageSize, searchTerm)
        return [f"[{dia.name}]({utils.make_url_from_id(dia.id)})" for dia in diagrams]

    return load_data

class DiagramsPaginator(Paginator):
    _original_message: discord.InteractionMessage = None

    def __init__(self, data_by_page, count: int, page_size: int = 5, timeout: float | None = 180):
        super().__init__(data_by_page, count, page_size, timeout)

    async def display(self, interaction: discord.Interaction, **kwargs):
        content = await self.render_page()
        await interaction.followup.send(content, view=self, **kwargs)
        self._original_message = await interaction.original_response()

    async def on_timeout(self):
        await self._original_message.edit(embed=None, view=None)
