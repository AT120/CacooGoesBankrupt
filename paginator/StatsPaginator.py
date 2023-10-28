from paginator.Paginator import Paginator
import discord
from repository.repository import database

class StatsPaginator(Paginator):
    _original_message: discord.InteractionMessage = None

    def __init__(
        self,
        client: discord.Client,
        after: int,
        count: int,
        page_size: int = 10,
        timeout: float | None = 180,
        prefix: str = "", 
    ):
        async def data_by_page(page):
            user_diagrams_count = await database.user_diagrams_count(page, page_size, after)
            content = []
            for dia in user_diagrams_count:
                user = client.get_user(dia.userId) # TODO: mentions
                if user != None:
                    content.append(f"@{user.name} {dia.userName} создал диаграмм: {dia.diagramsCount}") #TODO: проверить, пингует ли user.mention пользователя
                else:
                    content.append(f"{dia.userName} создал диаграмм: {dia.diagramsCount}") #TODO: проверить, пингует ли user.mention пользователя
            return content
        
        super().__init__(data_by_page, count, page_size, timeout, prefix)

    async def display(self, interaction: discord.Interaction):
        content = await self.render_page()
        await interaction.followup.send(content, view=self)
        self._original_message = await interaction.original_response()

    async def on_timeout(self):
        await self._original_message.edit(embed=None, view=None)
        
        