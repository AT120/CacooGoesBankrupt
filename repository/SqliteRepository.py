from .RepositoryBase import RepositoryBase, DiagramDTO
from sqlite4 import SQLite4
from pathlib import Path
from time import time

class SqliteRepository(RepositoryBase):
    _db: SQLite4
    def init(self, *params):
        databaseFile = params[0]
        if not Path(databaseFile).exists():
            raise FileNotFoundError()
        
        self._db = SQLite4(params[0])
        self._db.connect()

    def execute(self, query, parameters = ()):
        def execute_query():
            with self._db.connection:
                cursor = self._db.connection.cursor()
                cursor.execute(query, parameters)

        return self._db._queue_operation(execute_query)
        

    def execute_fetch(self, query, parameters = None):
        def execute_query():
            with self._db.connection:
                cursor = self._db.connection.cursor()
                cursor.execute(query, parameters)
                return cursor.fetchall()
        
        return self._db._queue_operation(execute_query)
            


    async def store_new_diagram(self, userId: int, diagramId: str, diagramName: str):
        self._db.insert("UserDiagram", 
                        {
                            "userId": userId, 
                            "diagramId": diagramId,
                            "diagramName": diagramName,
                            "timestamp": int(time())
                        })
        
    
    
    async def count_diagrams(self, userId: int, searchTerm: str | None = None) -> int:
        query = "SELECT COUNT(1) FROM UserDiagram WHERE userId = ? "
        params = [userId]
        if searchTerm != None:
            query += "AND diagramName LIKE ?"
            params.append(f"%{searchTerm}%")
        count = self.execute_fetch(query, params)
        return count[0][0]
    

    async def get_user_diagrams_page(self, userId: int, page: int, pageSize: int, searchTerm: str | None = None) -> list[DiagramDTO]:
        query = "SELECT diagramId, diagramName, timestamp FROM UserDiagram " \
                "WHERE userId = ? "
        params = [userId]
        if searchTerm != None:
            query += "AND diagramName LIKE ? "
            params.append(f"%{searchTerm}%")

        query += "ORDER BY timestamp DESC " \
                 "LIMIT ? OFFSET ?"
        params.append(pageSize)
        params.append(page * pageSize)
        page = self.execute_fetch(query, params)
        diagrams = [DiagramDTO(x[0], x[1], x[2]) for x in page]
        return diagrams
    
    
    async def user_have_diagram(self, userId: int, diagramId: str) -> bool:
        result = self.execute_fetch(
            "SELECT 1 FROM UserDiagram WHERE userId = ? AND diagramId = ?", 
            (userId, diagramId)
        )
        return len(result) > 0
    

    async def delete_diagram(self, diagramId: str):
        self.execute("DELETE FROM UserDiagram WHERE diagramId = ?", (diagramId,))


    async def cache_cacoo_data(self, organizationKey: str, folderId: int):
        self.execute("DELETE FROM CacooCache")
        # insert тут безопастный
        self._db.insert("CacooCache", { 
            "organizationKey": organizationKey,
            "folderId": folderId
        })
    
    async def load_cacoo_data(self) -> tuple[str, int] | None:
        cache = self._db.select("CacooCache")
        if len(cache) > 0:
            return cache[0]
        return None


    async def add_user_to_whitelist(self, userId: int, userName: str):
        self._db.insert("Whitelist", {"userId": userId, "userName": userName})
    

    async def user_in_whitelist(self, userId: int) -> bool:
        result = self.execute_fetch("SELECT 1 FROM Whitelist WHERE userId = ? ", (userId, ))
        return len(result) > 0


    async def remove_user_from_whitelist(self, userId: int):
        self.execute("DELETE FROM Whitelist WHERE userId = ? ", (userId, ))
    

    async def reset_white_list(self):
        self.execute("DELETE FROM Whitelist")

# RepositoryBase.register(SqliteRepository)