from repository.repository import database
import utils
from paginator.Paginator import Paginator
import discord

class DiagramsPaginator(Paginator):
    _original_message: discord.InteractionMessage = None

    def __init__(self, userId: int, searchTerm: str | None, count: int, page_size: int = 5, timeout: float | None = 180):
        async def load_data(page):
            diagrams = await database.get_diagrams_page(page, page_size, userId, searchTerm)
            return [f"[{dia.name}]({utils.make_url_from_id(dia.id)})" for dia in diagrams]
        
        super().__init__(load_data, count, page_size, timeout)

    async def display(self, interaction: discord.Interaction, **kwargs):
        content = await self.render_page()
        await interaction.followup.send(content, view=self, **kwargs)
        self._original_message = await interaction.original_response()

    async def on_timeout(self):
        await self._original_message.edit(embed=None, view=None)
