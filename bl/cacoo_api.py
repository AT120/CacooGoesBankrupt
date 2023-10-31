import aiohttp
import logging
from repository.repository import database 
import utils
import datetime
from config import config

class CacooException(Exception):
    def __init__(self, message, innerException = None) -> None:
        self.user_message = message
        super().__init__(innerException)

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
        await self._load_default_folder_id(config.get("cacoo-folder-name")) #TODO: in config
        await database.cache_cacoo_data(self._organizationKey, int(self._folderId))


    def __init__(self, apiKey) -> None:
        self._defaultParams["apiKey"] = apiKey


    def _url_to(self, endpoint: str) -> str:
        return self.CACOO_BASE_URL + endpoint
    

    async def _load_organization_key(self) -> str:
        url = self._url_to("organizations.json")
        async with self._session.get(url, params=self._defaultParams) as resp:
            if resp.status != 200:
                raise CacooException("Проблемы с доступом к Cacoo! попробуйте позже")

            organization = await resp.json(content_type=self._jsonMimetype)
            self._organizationKey = organization["result"][0]["key"]
            logging.info("organization key have been successfully loaded")


    async def _load_default_folder_id(self, name):
        url = self._url_to("folders.json")
        params = {"organizationKey": self._organizationKey}
        params |= self._defaultParams

        async with self._session.get(url, params=params) as resp:
            if resp.status != 200:
                raise CacooException("Проблемы с доступом к Cacoo! попробуйте позже")

            folders = await resp.json(content_type=self._jsonMimetype)
            folders = folders["result"]
            folder = next((fld for fld in folders if fld["folderName"] == name), None)
            if (folder == None):
                raise CacooException(f"folder with name {name} was not found!")
            self._folderId = folder["folderId"]
            
            logging.info("default folder id have been succesfully laoded")


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
            if resp.status == 400:
                raise CacooException("Попробуйте назвать диаграмму другим именем")
            if resp.status == 403:
                raise CacooException("Лимит диаграмм на мастер-аккаунте исчерпан")
            if resp.status == 404:
                logging.error("folder id does not exist!")
                raise CacooException("Приложение было некорректо сконфигурировано")
            if resp.status != 200:
                logging.error(f"diagram creation failed with {resp.status}. {diagramName=}, {self._folderId=}, {self._organizationKey}")
                raise CacooException("При обращении к Cacoo произошла непредвиденная ошибка")
            
            diagram = await resp.json(content_type=self._jsonMimetype)
            return diagram["url"]


    async def delete_diagram(self, diagramId):
        # diagramId = utils.extract_id_from_url(diagramUrl)
        url = self._url_to(f"diagrams/{diagramId}/delete.json")
        params = {"organizationKey": self._organizationKey}
        params |= self._defaultParams 
        async with self._session.get(url, params=params) as resp:
            if resp.status == 404:
                return # уже удалена, супер!  
            if resp.status == 403:
                raise CacooException("Диаграмма либо была создана не через меня, либо редактируется в текущий момент")
            if resp.status != 200:
                logging.error(f"diagram deletion failed with {resp.status}. {diagramId=}, {self._folderId=}, {self._organizationKey=}")
                raise CacooException("При обращении к Cacoo произошла непредвиденная ошибка")

    @utils.timeit
    async def diagram_last_use_time(self, diagramId: str) -> datetime.datetime:
        url = self._url_to(f"diagrams/{diagramId}.json")
        params = {"organizationKey": self._organizationKey}
        params |= self._defaultParams 
        async with self._session.get(url, params=params) as resp:
            if resp.status == 404:
                raise CacooException("Диаграмма не существует")
            if resp.status != 200:
                logging.error(f"diagram querying failed {resp.status}. {diagramId=}, {self._folderId=}, {self._organizationKey=}")
                raise CacooException("При обращении к Cacoo произошла непредвиденная ошибка")
            
            diagram = await resp.json(content_type=self._jsonMimetype)
            
            updateTime = datetime.datetime.strptime(diagram["updated"], "%a, %d %b %Y %H:%M:%S +0000")
            if diagram["updated"] == diagram["created"]:
                updateTime -= datetime.timedelta(hours=9)
            
            
            return updateTime.replace(tzinfo=datetime.timezone.utc)
        

cacoo = Cacoo(config.get("cacoo-api-key"))
    

    # async def ():
