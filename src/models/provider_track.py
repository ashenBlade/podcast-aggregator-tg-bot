from abc import ABC, abstractmethod
from dataclasses import dataclass
from sqlite3 import Connection
from typing import Any

from models.track_source import TrackSource


@dataclass
class ProviderTrack(ABC):
    """
    Трек, выпущенный конкретным провайдером.
    Используется при загрузке из БД
    """
    id: Any

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Имя провайдера трека.
        Лучше задавать константой, чтобы не было конфликтов с другими провайдерами
        :return: Имя провайдера
        """

    @abstractmethod
    async def save_track(self, track_id: int, connection: Connection):
        """
        Сохранить трек провайдера в БД
        :param track_id: ID исходного трека в БД
        :param connection: Объект подключения к БД
        """

    @abstractmethod
    def create_track_source(self) -> TrackSource:
        """
        Создать TrackSource трека текущего провайдера
        :return: Источник для трека этого провайдера
        """

    @abstractmethod
    async def check_saved(self, connection: Connection) -> bool:
        """
        Сохранен ли трек уже в БД
        :param connection: Объект соединения БД
        :return: True - трек для провайдера уже был сохранен, иначе False
        """

    def __hash__(self):
        return hash(self.provider_name)

    def __eq__(self, other):
        return self.provider_name == other.provider_name

