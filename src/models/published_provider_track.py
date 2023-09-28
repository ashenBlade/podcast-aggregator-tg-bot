from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta, date
from sqlite3 import Connection
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.podcast_provider import PodcastProvider

from models.provider_track import ProviderTrack


@dataclass
class PublishedProviderTrack(ProviderTrack, ABC):
    """
    Трек подкаста конкретного провайдера, загруженный из сети
    """
    title: str
    description: str
    duration: timedelta | None
    source_url: str
    publish_date: date
    provider: 'PodcastProvider'

    @abstractmethod
    async def try_find_linked_saved_track_id(self, connection: Connection) -> int | None:
        """
        Попытаться найти ID сохраненного трека, по ID трека провайдера,
        если трек уже сохранен в БД
        :param connection: Объект соединения с БД
        :return: ID сохраненного трека или ничего
        """

