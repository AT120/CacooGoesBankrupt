from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from utils import format_time
from typing import Sequence, Tuple

@dataclass
class DiagramDTO:
    id: str
    name: str
    creationTime: int
    updateTime: int | None = None

    def name_with_time(self) -> str:
        return f'"{self.name}" от {format_time(self.creationTime)}'

@dataclass
class UserDiagramDTO:
    diagramId: str
    diagramName: str
    creationTime: int
    updateTime: int | None
    userId: int
    userName: int

@dataclass
class UserDiagramsCount:
    userId: int
    userName: str
    diagramsCount: int


class RepositoryBase(ABC):
    @abstractmethod
    def init_connection(self, *params):
        pass

    @abstractmethod
    async def store_new_diagram(self, userId: int, diagramId: str, diagramName: str):
        pass

    @abstractmethod
    async def count_diagrams(self, userId: int, searchTerm: str | None = None) -> int:
        pass
    
    @abstractmethod
    async def get_diagrams_page(
        self, 
        page: int, 
        pageSize: int, 
        userId: int | None = None,
        searchTerm: str| None = None,
        after: int | None = None
    ) -> Sequence[DiagramDTO]:
        pass

    @abstractmethod
    async def get_diagrams_page_with_users(
        self, 
        page: int, 
        pageSize: int, 
        orderByUpdated: bool = False,
        userId: int | None = None,
        searchTerm: str| None = None,
        after: int | None = None
    ) -> Sequence[UserDiagramDTO]:
        pass
        

    @abstractmethod
    async def user_have_diagram(self, userId: int, diagramId: str) -> bool:
        pass

    @abstractmethod
    async def delete_diagram(self, userId: int, diagramId: str):
        pass

    @abstractmethod
    async def cache_cacoo_data(self, organizationKey: str, folderId: int):
        pass

    @abstractmethod
    async def load_cacoo_data(self) -> tuple[str, int]:
        pass

    @abstractmethod
    async def add_user_to_whitelist(self, userId: int, userName: str):
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

    @abstractmethod
    async def user_diagrams_count(
        self,
        page: int,
        pageSize: int, 
        after: int | None = None
    ) -> Sequence[UserDiagramsCount]:
        pass

    @abstractmethod
    async def count_users(self, after: int | None = None) -> int:
        pass

    @abstractmethod
    async def search_users(self, page: int, pageSize: int, searchTerm: str) -> Sequence[Tuple[int, str]]:
        pass

    @abstractmethod
    async def set_updatetime(self, diagramId: str, updatetime: int):
        pass