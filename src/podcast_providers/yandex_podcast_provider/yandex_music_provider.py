import logging
from datetime import datetime, date
from json import JSONDecodeError

import aiohttp
from pydantic import ValidationError

from models.podcast_provider import PodcastProvider
from models.provider_track import ProviderTrack
from .album import Album


_logger = logging.getLogger('YandexPodcastProvider')


class YandexMusicProvider(PodcastProvider):
    album: int

    def __init__(self, album: int):
        self.album = album

    @property
    def load_album_url(self) -> str:
        return (
            f'https://music.yandex.ru/handlers/album.jsx?album={self.album}' 
            f'&lang=ru&external-domain=music.yandex.ru&overembed=false'
        )

    def create_load_track_url(self, track_id: int):
        return f'https://music.yandex.ru/album/{self.album}/track/{track_id}'

    async def get_track_published_in_specified_date(self, publish_date: date) -> list[ProviderTrack]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.load_album_url) as response:
                    album = Album(**(await response.json()))
                    track = album.get_track_published_in(publish_date)
                    if not track:
                        return None

                    return ProviderTrack(
                            id=track.id,
                            name=track.title,
                            publication_date=track.publication_date,
                            description=track.short_description,
                            duration=track.duration,
                            source_url=self.create_load_track_url(track.id),
                            tags=[],
                        )
        except ValidationError as validation_error:
            _logger.error('Ошибка при создании объекта альбома', exc_info=validation_error)
        except JSONDecodeError as json_decode_error:
            _logger.error('Ошибка парсинга пришедшего json', exc_info=json_decode_error)
        except Exception as e:
            _logger.error('Ошибка во время запроса к серверам яндекса', exc_info=e)

        return []
