from abc import ABC, abstractmethod
from datetime import date

from models.provider_track import ProviderTrack


class PodcastProvider(ABC):
    name: str

    @abstractmethod
    async def get_track_published_in_specified_date(self, publish_date: date) -> ProviderTrack | None:
        """
        Скачать трек подкаста, который был выложен в указанную дату (без времени).
        Предполагается, что все треки от разных провайдеров, выпущенные в один день относятся к одному и тому же треку
        """
