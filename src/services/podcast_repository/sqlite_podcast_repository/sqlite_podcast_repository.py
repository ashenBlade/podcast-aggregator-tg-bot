import datetime
import json
import logging
import sqlite3
from datetime import datetime

from abstractions.podcast_repository import PodcastRepository
from models.podcast import Podcast
from models.track import Track
from services.podcast_providers import YandexMusicProvider
from services.podcast_providers.yandex_podcast_provider.yandex_provider_info import YandexProviderInfo

_logger = logging.getLogger(__name__)


def parse_podcast_row(row: tuple):
    id, name, description, tags_str, yc_album = row
    providers = [YandexMusicProvider(yc_album)] if yc_album else []
    return Podcast(
        id=id,
        name=name,
        description=description,
        providers=providers,
        tags=json.loads(tags_str) if tags_str else []
    )


class SqlitePodcastRepository(PodcastRepository):
    database: str

    def __init__(self, database: str):
        self.database = database

    async def get_all_podcasts(self) -> list[Podcast]:
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute(
                'select p.id, p.name, p.description, ('
                ' case count(t.id) when 0 then null else json_group_array(t.tag) end'
                ') as tags, ymp.album '
                'from podcasts p '
                'left join podcast_tag pt on p.id = pt.podcast_id '
                'left join tags t on pt.tag_id = t.id '
                'left join yandex_music_providers ymp on p.id = ymp.podcast_id '
                'group by p.id, p.name, p.description;'
            )

            return [
                parse_podcast_row(row)
                for row
                in cursor.fetchall()
            ]

    async def is_track_already_sent(self, track: Track) -> bool:
        """
        Был ли уже отправлен трек или нет.
        Если хотя бы один из провайдеров отправлен, возвращает true
        """
        if not track.provider_infos:
            return

        with sqlite3.connect(self.database) as connection:
            for provider_info in track.provider_infos:
                try:
                    if isinstance(provider_info, YandexProviderInfo):
                        cursor = connection.execute(
                            'select 1 from yandex_music_published_tracks where track_id = $1',
                            (provider_info.id,)
                        )
                        exists = cursor.fetchone()
                        if exists and exists[0]:
                            return True
                    else:
                        _logger.warning('Неизвестный тип информации о провайдере: %s', provider_info)
                except Exception as e:
                    _logger.error('Ошибка во время обновления данных об отправленных треках', exc_info=e)
            return False

    async def mark_track_sent(self, track: Track):
        """
        Пометить трек как отправленный, чтобы дальше не отправлять
        """
        if not track.provider_infos:
            return

        with sqlite3.connect(self.database) as connection:
            for provider_info in track.provider_infos:
                try:
                    if isinstance(provider_info, YandexProviderInfo):
                        connection.execute(
                            'insert into yandex_music_published_tracks(track_id, published_time) '
                            'values ($1, $2) on conflict do nothing;',
                            (provider_info.id, datetime.now())
                        )
                        _logger.info('Трек из яндекс музыки id %i сохранен как отправленный', provider_info.id)
                    else:
                        _logger.warning('Неизвестный тип информации о провайдере: %s', provider_info)
                except Exception as e:
                    _logger.error('Ошибка во время обновления данных об отправленных треках', exc_info=e)

