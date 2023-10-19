import aiohttp
import asyncio

class Cacoo:
    CACOO_BASE_URL = "https://cacoo.com/api/v1/"
    defaultParams = {"apiKey": ""}
    _session: aiohttp.ClientSession = None

    async def create_session(self, loop): 
        self._session = aiohttp.ClientSession()
        yield
        await self._session.close()

    
    def __init__(self, apiKey, loop) -> None:
        self.defaultParams["apiKey"] = apiKey
        # self.create_session(loop)

    def _url_to(self, endpoint: str) -> str:
        return self.CACOO_BASE_URL + endpoint
    

    async def get_organization_key(self) -> str:
        url = self._url_to("organizations.json")
        # async with aiohttp.ClientSession() as __session__:
        async with self._session.get(url, params=self.defaultParams) as resp:
            respj = await resp.json()
            return respj["result"][0]["key"]
        
            # async with __session__.get(url, params=self.defaultParams) as resp:



    async def get_user_folder(userName):
        pass

    async def create_diagram(folderId):
        pass

    # async def ():