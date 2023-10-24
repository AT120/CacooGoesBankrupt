import aiohttp
import asyncio
import logging
import utils
from repository.repository import database 

class Cacoo:
    CACOO_BASE_URL = "https://cacoo.com/api/v1/"
    _defaultParams = {"apiKey": ""}
    _folderId = ""
    _session: aiohttp.ClientSession = None
    _organizationKey = ""
    _jsonMimetype = "text/javascript;charset=utf-8"


    async def initialize(self, app): 
        self._session = aiohttp.ClientSession()
        
        if not await self._load_defaults_from_cache():
            await self._load_defaults_from_cacoo()

        yield
        await self._session.close()

    async def reset_cache(self):
        await self._load_defaults_from_cacoo()

    async def _load_defaults_from_cache(self) -> bool:
        cache = await database.load_cacoo_data()
        if cache is None:
            return False
        
        self._organizationKey = cache[0]
        self._folderId = str(cache[1])
        logging.info("loaded cacoo defaults from database cache")
        return True


    async def _load_defaults_from_cacoo(self):
        await self._load_organization_key()
        await self._load_default_folder_id("diagrams") #TODO: in config
        await database.cache_cacoo_data(self._organizationKey, int(self._folderId))


    def __init__(self, apiKey) -> None:
        self._defaultParams["apiKey"] = apiKey


    def _url_to(self, endpoint: str) -> str:
        return self.CACOO_BASE_URL + endpoint
    

    def _check_response(self, resp: aiohttp.ClientResponse):
        if (resp.status != 200):
            raise ValueError(f"Request failed with status {resp.status}")


    async def _load_organization_key(self) -> str:
        url = self._url_to("organizations.json")
        async with self._session.get(url, params=self._defaultParams) as resp:
            if resp.status != 200:
                raise ValueError(f"Request failed with status {resp.status}") #TODO: change exception

            organization = await resp.json(content_type=self._jsonMimetype)
            self._organizationKey = organization["result"][0]["key"]
            logging.info("organization key have been successfully loaded")


    async def _load_default_folder_id(self, name):
        url = self._url_to("folders.json")
        params = {"organizationKey": self._organizationKey}
        params |= self._defaultParams

        async with self._session.get(url, params=params) as resp:
            self._check_response(resp) #TODO: не надо так

            folders = await resp.json(content_type=self._jsonMimetype)
            folders = folders["result"]
            folder = next((fld for fld in folders if fld["folderName"] == name), None)
            if (folder == None):
                raise ValueError(f"folder with name {name} was not found!") #TODO:
            self._folderId = folder["folderId"]
            
            logging.info("default folder id have been succesfully laoded")
            

    async def create_user_folder(userName):
        pass


    async def get_user_folder(userName):
        pass


    async def create_diagram(self, diagramName) -> str:
        url = self._url_to("diagrams/create.json")
        params = {
            "organizationKey": self._organizationKey,
            "folderId": self._folderId,
            "title": diagramName,
            "security": "public"
        }
        params |= self._defaultParams
        async with self._session.get(url, params=params) as resp:
            if resp.status != 200: #TODO: error handling
                raise ValueError(f"Diagram creation failed with status code {resp.status}")
            
            diagram = await resp.json(content_type=self._jsonMimetype)
            return diagram["url"]


    async def delete_diagram(self, diagramUrl):
        diagramId = utils.extract_id_from_url(diagramUrl)
        url = self._url_to(f"diagrams/{diagramId}/delete.json")
        params = {"organizationKey": self._organizationKey}
        params |= self._defaultParams 
        async with self._session.get(url, params=params) as resp:
            if resp.status != 200:
                raise ValueError(f"Diagram deletion failed with status code {resp.status}")

    # async def ():
