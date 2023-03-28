import logging
from datetime import date
from json import JSONDecodeError

import aiohttp
from pydantic import ValidationError

from models.podcast_provider import PodcastProvider
from models.published_provider_track import PublishedProviderTrack
from podcast_providers.yandex_podcast_provider.album import Album

from podcast_providers.yandex_podcast_provider.yandex_published_provider_track import YandexPublishedProviderTrack

_logger = logging.getLogger(__name__)


class YandexMusicProvider(PodcastProvider):
    album: int

    def __init__(self, album: int):
        self.album = album

    @property
    def name(self):
        return 'Яндекс.Музыка'

    def create_source_url(self, track_id):
        return f'https://music.yandex.ru/album/{self.album}/track/{track_id}?activeTab=track-list&dir=desc'

    @property
    def load_album_url(self) -> str:
        return f'https://api.music.yandex.net/albums/{self.album}/with-tracks'

    async def get_track_published_at(self, publish_date: date) -> PublishedProviderTrack | None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.load_album_url) as response:
                    json = await response.json()

            album = Album(**json['result'])
            if not album:
                return None

            track = album.get_track_published_in(publish_date)
            if not track:
                return None
            return YandexPublishedProviderTrack(
                id=track.id,
                title=track.title,
                publish_date=track.publication_date,
                description=track.short_description,
                duration=track.duration,
                source_url=self.create_source_url(track.id),
                provider=self,
            )
        except ValidationError as validation_error:
            _logger.error('Ошибка при создании объекта альбома', exc_info=validation_error)
        except JSONDecodeError as json_decode_error:
            _logger.error('Ошибка парсинга пришедшего json', exc_info=json_decode_error)
        except Exception as e:
            _logger.error('Ошибка во время запроса к серверам яндекса', exc_info=e)

    def __str__(self) -> str:
        return f'YandexMusicProvider(album={self.album!r})'

    def __repr__(self) -> str:
        return f'YandexMusicProvider(album={self.album!r})'


