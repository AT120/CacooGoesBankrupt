from repository.repository import database
from bl.cacoo_api import cacoo
async def delete_diagram(userId: int, diagramId: str) -> bool:
    if not await database.user_have_diagram(userId, diagramId):
        return False
    
    try:
        await cacoo.delete_diagram(diagramId)
        await database.delete_diagram(userId, diagramId)
    except:
        return False
    
    return True