from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass

@dataclass
class DiagramDTO:
    id: str
    name: str
    creationTime: int


class RepositoryBase(ABC):
    @abstractmethod
    def init(self, *params):
        pass

    @abstractmethod
    async def store_new_diagram(self, userId: int, diagramId: str, diagramName: str):
        pass

    @abstractmethod
    async def count_diagrams(self, userId: int, searchTerm: str | None = None) -> int:
        pass
    
    @abstractmethod
    async def get_user_diagrams_page(self, userId: int, page: int, pageSize: int, searchTerm: str| None = None) -> list[DiagramDTO]:
        pass

    @abstractmethod
    async def user_have_diagram(self, userId: int, diagramId: str) -> bool:
        pass

    @abstractmethod
    async def delete_diagram(self, diagramId: str):
        pass

    @abstractmethod
    async def cache_cacoo_data(self, organizationKey: str, folderId: int):
        pass

    @abstractmethod
    async def load_cacoo_data(self) -> tuple[str, int]:
        pass

    @abstractmethod
    async def add_user_to_whitelist(self, userId: int):
        pass

    @abstractmethod
    async def user_in_whitelist(self, userId: int) -> bool:
        pass

    @abstractmethod
    async def remove_user_from_whitelist(self, userId: int):
        pass

    @abstractmethod
    async def reset_white_list(self):
        pass
