import asyncio
from paginator.DeletionPaginator import DeletionPaginator
import discord
from repository.repository import database
from utils import format_time, make_url_from_id, days_since
from bl.shared_diagram_logic import delete_diagram

class UnusedDiagramsPaginator(DeletionPaginator):
    _original_message: discord.InteractionMessage = None
    _client: discord.Client = None
    _diagrams_to_delete = []
    _userIds = {}

    def __init__(
        self,
        client: discord.Client,
        count: int,
        page_size: int = 10,
        timeout: float | None = 180,
        prefix: str = "", 
    ):
        super().__init__(count, page_size, timeout, prefix)
        self._client = client
    

    async def on_delete(self, values) -> bool:
        results = await asyncio.gather(
            *[delete_diagram(self._userIds[dia], dia) for dia in values]
        )
        return not (False in results)


    async def data_by_page(self, page):
        content = ""
        diagrams = await database.get_diagrams_page_with_users(page, self._page_size, True)
        prevSegmentMark = None
        
        selectOptions = []
        self._userIds = {}
        for dia in diagrams:
            self._userIds[dia.diagramId] = dia.userId
            segmentMsg, segmentMark = self._get_segment(dia.updateTime)
            if segmentMark != prevSegmentMark:
                content += "### " + segmentMsg + " назад:\n"
                prevSegmentMark = segmentMark

            user = self._client.get_user(dia.userId)

            selectOptions.append(discord.SelectOption(
                label=f"{dia.diagramName}; дней с последнего обновления: {days_since(dia.updateTime)}"[:100],
                value=dia.diagramId
            ))
            if user != None:
                content +=  f'- [{dia.diagramName}]({make_url_from_id(dia.diagramId)}) ; ' \
                            f'диаграмма создана {user.mention}; последнее обновление: {format_time(dia.updateTime)} ; ' \
                            f'примерно дней назад: {days_since(dia.updateTime)} \n'
            else:
                content +=  f'- [{dia.diagramName}]({make_url_from_id(dia.diagramId)}) ; ' \
                            f'диаграмма создана {dia.userName}; последнее обновление: {format_time(dia.updateTime)} ; ' \
                            f'примерно дней назад: {days_since(dia.updateTime)}\n'
                
        self.reload_selector_options(selectOptions)
        return content
    

    def _get_segment(self, timestamp: int):
        days = days_since(timestamp) 
        if days > 30:
            months = days // 30
            if months % 10 == 1:
                return f"более {months} месяца", str(months) + "m"
            else:
                return f"более {months} месяцев", str(months) + "m"
                
        elif days > 7:
            weeks = days // 7
            if weeks == 1:
                return "более 1 недели", "1w"
            else:
                return f"более {weeks} недель", str(weeks) + "w"
            
        return "менее 1 недели", "0w"  
            


    async def display(self, interaction: discord.Interaction):
        content = await self.render_page()
        await interaction.followup.send(content, view=self, suppress_embeds=True, ephemeral=True)
        self._original_message = await interaction.original_response()


    async def on_timeout(self):
        #TODO: ты не туда таймаутишь
        await self._original_message.edit(embed=None, view=None)
        
