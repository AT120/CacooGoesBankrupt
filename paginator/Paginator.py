from typing import Optional
import discord
import math
from collections.abc import Awaitable
from decorators.maintenance import lock_on_maintenance

class Paginator(discord.ui.View):
    _current_page = 0
    _count = 0
    _page_size = 0
    _last_page = 0
    _prefix = ""


    def __init__(self, count: int, page_size: int = 5, timeout: float | None = 180, prefix: str = ""):
        super().__init__(timeout=timeout)
        self._page_size = page_size
        self._count = count
        if count == 0:
            self._last_page = 0
        else:
            self._last_page = math.ceil(count / page_size) - 1

        self._prefix = prefix
        self._update_button_status()

    async def data_by_page(self, page: int) -> str:
        return ""

    async def render_page(self) -> str:
        content = self._prefix
        content += await self.data_by_page(self._current_page)

        if self._current_page == self._last_page:
            elementsShown = self._count 
        else:
            elementsShown = self._page_size * (self._current_page + 1)

        content += f"_{elementsShown}/{self._count}_"
        return content


    def _update_button_status(self):
        self.children[0].disabled = (self._current_page <= 0)
        self.children[1].disabled = (self._current_page >= self._last_page)


    @discord.ui.button(emoji="\u23EA")
    @lock_on_maintenance #TODO: а это точно работает?
    async def _prev_button_handler(self, interaction: discord.Interaction, pressed: discord.ui.Button):
        self._current_page -= 1
        self._update_button_status()
        
        newContent = await self.render_page()
        await interaction.response.edit_message(content=newContent, view=self)


    @discord.ui.button(emoji="\u23E9")
    @lock_on_maintenance
    async def _next_button_handler(self, interaction: discord.Interaction, pressed: discord.ui.Button):
        self._current_page += 1
        self._update_button_status()

        newContent = await self.render_page()
        # enable prev button 
        await interaction.response.edit_message(content=newContent, view=self)