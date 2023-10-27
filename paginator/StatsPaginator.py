from paginator.Paginator import Paginator
import discord

class StatsPaginator(Paginator):

    def __init__(self, data_by_page, count: int, page_size: int = 5, timeout: float | None = 180):
        super().__init__(data_by_page, count, page_size, timeout)

    async def display(self, interaction: discord.Interaction):
        content = await self.render_page()
        await interaction.followup.send(content, view=self)
        
        