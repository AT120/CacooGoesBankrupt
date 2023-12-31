import asyncio
from paginator.Paginator import Paginator
import discord
from consts import Reactions
import math
import utils
class DeletionPaginator(Paginator):
    _original_message: discord.InteractionMessage = None
    _selectorInd = None
    _confirmationButtonInd = 0
    _values_to_delete = []

    def __init__(
        self,
        count: int,
        page_size: int = 10,
        timeout: float | None = 180,
        prefix: str = "", 
    ):
        super().__init__(count, page_size, timeout, prefix)
        
        self._confirmationButtonInd = len(self._children) - 1
        # self._selectorInd = len(self._children)
        # self._children.append(None)

    
    async def on_delete(self, values) -> int:
        pass

    def reload_selector_options(self, newOptions):
        self._children[self._confirmationButtonInd].disabled = True
        if (self._selectorInd != None):
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
            self.add_item(selector)
            self._selectorInd = len(self.children) - 1


    async def _delete_selector_callback(self, interaction: discord.Interaction, select: discord.ui.Select = None):
        selector = self._children[self._selectorInd]
        if len(selector.values) == 0:
            self._children[self._confirmationButtonInd].disabled = True
        else:
            self._children[self._confirmationButtonInd].disabled = False

        for option in selector.options:
            option.default = (option.value in selector.values)

        self._values_to_delete = selector.values
        await interaction.response.edit_message(view=self)    


    @discord.ui.button(emoji="\U0001f5d1", disabled=True, row=2, style=discord.ButtonStyle.danger)
    async def _delete_button_callback(self, interaction: discord.Interaction, pressed: discord.ui.Button):

        self._children[self._confirmationButtonInd].disabled = True
        await interaction.response.edit_message(content="Удаляю...", view=self)

        deleted = await self.on_delete(self._values_to_delete)
        should_be_deleted = len(self._values_to_delete)
        self._values_to_delete = []

        self._count -= deleted
        self._last_page = math.ceil(self._count / self._page_size) - 1
        self._current_page = 0
        self._update_button_status()
        
        newContent = await self.render_page()
        await interaction.edit_original_response(content=newContent, view=self)        

        if deleted == should_be_deleted:
            await interaction.followup.send(Reactions.positive + " Успешно удалено", ephemeral=True)
        else:
            await interaction.followup.send(Reactions.negative + " При удалении некоторых диаграмм произошла ошибка", ephemeral=True)

            

        
