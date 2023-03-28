from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

from models.published_provider_track import PublishedProviderTrack


@dataclass
class PodcastProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Название провайдера подкаста
        """

    @abstractmethod
    async def get_track_published_at(self, publish_date: date) -> PublishedProviderTrack | None:
        """
        Получить трек выпущенный в указанную дату
        :param publish_date: Дата публикации трека
        :return: Выпущенный трек или ничего
        """


