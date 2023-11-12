from .RepositoryBase import *
from sqlite4 import SQLite4
from pathlib import Path
from time import time
from typing import Sequence

class SqliteRepository(RepositoryBase):
    _db: SQLite4
    def init_connection(self, *params):
        databaseFile = params[0]
        
        self._db = SQLite4(params[0])
        self._db.connect()

        self._init_database()


    def _init_database(self):
        self._db.create_table("CacooCache", [
            '"organizationKey"	TEXT NOT NULL',
            '"folderId"	INTEGER NOT NULL'
        ])
        self._db.create_table("UserDiagram", [
            '"userId"	INTEGER NOT NULL',
            '"diagramId"	TEXT NOT NULL UNIQUE',
            '"diagramName"	TEXT',
            '"created"	INTEGER',
            '"updated"	INTEGER'
        ])
        self._db.create_table("Users", [
            '"userId"	INTEGER NOT NULL UNIQUE',
            '"userName"	TEXT',
            '"whitelisted"	INTEGER DEFAULT 1',
        ])


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
    

    def build_predicate(self, predicates):
        if len(predicates) == 0:
            return ""

        return "WHERE " + " AND ".join(predicates)


    async def store_new_diagram(self, userId: int, diagramId: str, diagramName: str):
        self._db.insert("UserDiagram", 
                        {
                            "userId": userId, 
                            "diagramId": diagramId,
                            "diagramName": diagramName,
                            "created": int(time())
                        })
        
    
    
    async def count_diagrams(
        self,
        userId: int | None = None,
        searchTerm: str | None = None,
        after: int | None = None
    ) -> int:
        query = "SELECT COUNT(1) FROM UserDiagram "
        predicates = []
        params = []

        if userId != None:
            predicates.append("userId = ?")
            params.append(userId)

        if searchTerm != None:
            predicates.append("diagramName LIKE ?")
            params.append(f"%{searchTerm}%")

        if after != None:
            predicates.append("created > ?")
            params.append(after)

        query += self.build_predicate(predicates)

        count = self.execute_fetch(query, params)
        return count[0][0]
    

    async def get_diagrams_page(
        self, 
        page: int, 
        pageSize: int, 
        userId: int | None = None, 
        searchTerm: str | None = None,
        after: int | None = None
    ) -> Sequence[DiagramDTO]:
        params = []
        query = "SELECT diagramId, diagramName, created, updated FROM UserDiagram " 
                
        predicates = []
        if userId != None:
            predicates.append("userId = ?")
            params.append(userId)

        if after != None:
            predicates.append("created > ?")
            params.append(after)

        if searchTerm != None:
            predicates.append("diagramName LIKE ?")
            params.append(f"%{searchTerm}%")
        
        query += self.build_predicate(predicates)
        query += " ORDER BY created DESC" \
                 " LIMIT ? OFFSET ?"
        
        params.append(pageSize)
        params.append(page * pageSize)
        page = self.execute_fetch(query, params)
        diagrams = [DiagramDTO(x[0], x[1], x[2], x[3]) for x in page]
        return diagrams
    
    
    async def get_diagrams_page_with_users(
        self, 
        page: int, 
        pageSize: int, 
        orderByUpdated: bool = False,
        userId: int | None = None,
        searchTerm: str| None = None,
        after: int | None = None,
    ) -> Sequence[UserDiagramDTO]:
        params = []
        query = "SELECT diagramId, diagramName, created, updated, UserDiagram.userId, userName FROM UserDiagram " \
                "JOIN Users on UserDiagram.userId = Users.userId "
                
        predicates = []
        if userId != None:
            predicates.append("UserDiagram.userId = ?")
            params.append(userId)

        if after != None:
            predicates.append("created > ?")
            params.append(after)

        if searchTerm != None:
            predicates.append("diagramName LIKE ?")
            params.append(f"%{searchTerm}%")
        
        query += self.build_predicate(predicates)
        if orderByUpdated:
            query += " ORDER BY updated"
        else:
            query += " ORDER BY created DESC"

        query += " LIMIT ? OFFSET ?"
        
        params.append(pageSize)
        params.append(page * pageSize)
        page = self.execute_fetch(query, params)
        diagrams = [UserDiagramDTO(x[0], x[1], x[2], x[3], x[4], x[5]) for x in page]
        return diagrams
    
    
    async def user_have_diagram(self, userId: int, diagramId: str) -> bool:
        result = self.execute_fetch(
            "SELECT 1 FROM UserDiagram WHERE userId = ? AND diagramId = ?", 
            (userId, diagramId)
        )
        return len(result) > 0
    

    async def delete_diagram(self, userId: int, diagramId: str):
        self.execute("DELETE FROM UserDiagram WHERE diagramId = ?", (diagramId,))
        if (
            await self.count_diagrams(userId=userId) == 0 and
            not await self.user_in_whitelist(userId)
        ):
            self.execute("DELETE FROM Users WHERE userId = ?", (userId,))


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
        self._db.insert("Users", {"userId": userId, "userName": userName})
        self.execute("UPDATE Users SET whitelisted = 1 WHERE userId = ?", (userId,))
    

    async def user_in_whitelist(self, userId: int) -> bool:
        result = self.execute_fetch("SELECT whitelisted FROM Users WHERE userId = ? ", (userId, ))
        return len(result) > 0 and result[0][0]


    async def remove_user_from_whitelist(self, userId: int):
        self.execute("UPDATE Users SET whitelisted = 0 WHERE userId = ? ", (userId, ))
    

    async def reset_white_list(self):
        self.execute("UPDATE Users SET whitelisted = 0")


    async def user_diagrams_count(
            self,
            page: int, 
            pageSize: int, 
            after: int | None = None
        ) -> Sequence[UserDiagramsCount]:
        query = "SELECT UserDiagram.userId, userName, COUNT(diagramId) FROM UserDiagram " \
                "INNER JOIN Users on UserDiagram.userId = Users.userId "
        
        params = []
        if after != None:
            query += "WHERE created > ? "
            params.append(after)

        query += "GROUP BY UserDiagram.userId " \
                 "ORDER BY COUNT(diagramId) DESC " \
                 "LIMIT ? OFFSET ?"
        
        params.append(pageSize)
        params.append(page * pageSize)
        result = self.execute_fetch(query, params)
        return [UserDiagramsCount(i[0], i[1], i[2]) for i in result]
    
    async def count_users(self,  after: int | None = None) -> int:
        query = "SELECT COUNT(DISTINCT userId) FROM UserDiagram "
        params = []
        if (after != None):
            query += "WHERE created > ?"
            params.append(after)

        res = self.execute_fetch(query, params)
        return res[0][0] 
    

    async def search_users(self, page: int, pageSize: int, searchTerm: str) -> Sequence[Tuple[int, str]]:
        query = "SELECT userId, userName FROM Users " \
                "WHERE userName LIKE ? " \
                "LIMIT ? OFFSET ? "
        params = [f"%{searchTerm}%", pageSize, page*pageSize]
        return self.execute_fetch(query, params)


    async def set_updatetime(self, diagramId: str, updatetime: int):
        self.execute("UPDATE UserDiagram SET updated = ? WHERE diagramId = ?", (updatetime, diagramId))

# RepositoryBase.register(SqliteRepository)