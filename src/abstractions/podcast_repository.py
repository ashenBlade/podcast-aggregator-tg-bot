from abc import ABC, abstractmethod

from models import Podcast


class PodcastRepository(ABC):
    """Интерфейс для работы с объектами подкастов"""

    @abstractmethod
    async def get_all_podcasts(self) -> list[Podcast]:
        """
        Получить все подкасты из репозитория.
        Для дальнейшей загрузки треков от провайдеров
        :return: list[Podcast]
        """
