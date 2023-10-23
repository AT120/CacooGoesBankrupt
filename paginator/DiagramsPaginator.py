from repository.repository import database
import utils

def get_data_loader(userId: int, pageSize: int, searchTerm: str | None):
    async def load_data(page):
        diagrams = await database.get_user_diagrams_page(userId, page, pageSize, searchTerm)
        return [f"[{dia.name}]({utils.make_url_from_id(dia.id)})" for dia in diagrams]

    return load_data