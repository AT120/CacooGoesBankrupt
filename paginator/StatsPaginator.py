from paginator.Paginator import Paginator
import discord
from repository.repository import database

class StatsPaginator(Paginator):
    _original_message: discord.InteractionMessage = None
    _client: discord.Client = None
    _after = 0
    
    def __init__(
        self,
        client: discord.Client,
        after: int,
        count: int,
        page_size: int = 10,
        timeout: float | None = 180,
        prefix: str = "", 
    ):
        self._after = after
        self._client = client
        super().__init__(count, page_size, timeout, prefix)


    async def data_by_page(self, page):
        user_diagrams_count = await database.user_diagrams_count(page, self._page_size, self._after)
        content = ""
        for dia in user_diagrams_count:
            #TODO: не показывать челов с 0 диаграмм
            user = self._client.get_user(dia.userId)
            if user != None:
                content += f"- {user.mention} ({dia.userName}) создал диаграмм: {dia.diagramsCount}\n" 
            else:
                content += f"- {dia.userName} создал диаграмм: {dia.diagramsCount}\n"
        return content


    async def display(self, interaction: discord.Interaction):
        content = await self.render_page()
        await interaction.followup.send(content, view=self)
        self._original_message = await interaction.original_response()

    async def on_timeout(self):
        await self._original_message.edit(embed=None, view=None)
        
        