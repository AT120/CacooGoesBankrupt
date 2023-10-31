import json
from sys import argv
import os
from pathlib import Path
from utils import get_application_dir


class AppConfig():
    _configData = None
    def __init__(self) -> None:
        config = get_application_dir().joinpath("config.json")

        if (not config.exists()):
            raise FileNotFoundError("Unable to find config.json")

        with open(config) as conf:
            self._configData = json.load(conf)

    def get(self, key: str):
        return self._configData[key]


config = AppConfig()