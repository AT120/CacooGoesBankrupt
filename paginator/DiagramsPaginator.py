from repository.repository import database
import utils
from paginator.DeletionPaginator import DeletionPaginator
import discord
import asyncio
from bl.non_interactive_logic import delete_diagram
class DiagramsPaginator(DeletionPaginator):
    _original_message: discord.InteractionMessage = None
    _user_id = 0
    _search_term = ""

    def __init__(self, userId: int, searchTerm: str | None, count: int, page_size: int = 5, timeout: float | None = 180):
        self._user_id = userId
        self._search_term = searchTerm
        super().__init__(count, page_size, timeout)
    
    async def data_by_page(self, page: int) -> str:
        #TODO: какое-нибудь сообщение при 0
        diagrams = await database.get_diagrams_page(page, self._page_size, self._user_id , self._search_term)
        content = ""
        selectOptions = []
        for dia in diagrams:
            selectOptions.append(discord.SelectOption(
                label=dia.name,
                value=dia.id
            ))
            content += f"- [{dia.name}]({utils.make_url_from_id(dia.id)})\n"
            self.reload_selector_options(selectOptions) 
        return content
    
    async def on_delete(self, values) -> bool:
        results = await asyncio.gather(
            *[delete_diagram(self._user_id, dia) for dia in values]
        )
        return sum(results)

    async def display(self, interaction: discord.Interaction, **kwargs):
        content = await self.render_page()
        await interaction.followup.send(content, view=self, **kwargs)
        self._original_message = await interaction.original_response()

    async def on_timeout(self):
        await self._original_message.edit(embed=None, view=None)
