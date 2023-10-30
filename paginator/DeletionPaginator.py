import asyncio
from typing import Optional
from discord.utils import MISSING
from paginator.Paginator import Paginator
import discord
from repository.repository import database
from utils import format_time, make_url_from_id, days_since
from bl.shared_diagram_logic import delete_diagram
from consts import Reactions


class UnusedDiagramsPaginator(Paginator):
    _original_message: discord.InteractionMessage = None
    _selectorInd = 0
    _confirmationButtonInd = 0
    _diagrams_to_delete = []
    _userIds = {}

    def __init__(
        self,
        count: int,
        page_size: int = 10,
        timeout: float | None = 180,
        prefix: str = "", 
    ):
        super().__init__(count, page_size, timeout, prefix)
        
        self._confirmationButtonInd = len(self._children) - 1
        self._selectorInd = len(self._children)
        self._children.append(None)

    
    async def on_delete(value) -> bool:
        pass

    def reload_selector_options(self, newOptions):
        if (self._children[self._selectorInd] != None):
            self._children[self._selectorInd].options = newOptions
            self._children[self._selectorInd].max_values = len(newOptions)
        else:
            selector = discord.ui.Select(
                placeholder="Удаляем что-нибудь?",
                min_values=0,
                max_values=len(newOptions),
                options=newOptions
            )
            selector.callback = self._delete_selector_callback


    

    async def _delete_selector_callback(self, interaction: discord.Interaction, select: discord.ui.Select = None):
        selector = self._children[self._selectorInd]
        if len(selector.values) == 0:
            self._children[self._confirmationButtonInd].disabled = True
        else:
            self._children[self._confirmationButtonInd].disabled = False

        for option in selector.options:
            option.default = (option.value in selector.values)

        self._diagrams_to_delete = selector.values
        await interaction.response.edit_message(view=self)    


    @discord.ui.button(emoji="\U0001f5d1", disabled=True, row=2, style=discord.ButtonStyle.danger)
    async def _delete_button_callback(self, interaction: discord.Interaction, pressed: discord.ui.Button):
        await interaction.response.edit_message(content="Удаляю...")
        results = await asyncio.gather(
            *[delete_diagram(interaction, self._userIds[dia], dia) for dia in self._diagrams_to_delete]
        )
        if False in results:
            await interaction.followup.send(Reactions.negative + "При удалении некоторых диаграмм произошла ошибка")
        else:
            await interaction.followup.send(Reactions.positive + "Успешно удалено")
            

        
