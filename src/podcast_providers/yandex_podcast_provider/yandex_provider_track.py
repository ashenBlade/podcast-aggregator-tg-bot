import logging
from dataclasses import dataclass
from sqlite3 import Connection

from models.provider_track import ProviderTrack
from models.track_source import TrackSource
from podcast_providers.yandex_podcast_provider import constants
from podcast_providers.yandex_podcast_provider.helpers import create_track_source_url

_logger = logging.getLogger(__name__)


@dataclass
class YandexProviderTrack(ProviderTrack):
    async def check_saved(self, connection: Connection) -> bool:
        exists, = connection.execute((
            'select exists(select 1 from tracks where yc_track_id = ?)'
        ), (self.id,)).fetchone()
        return exists

    @property
    def provider_name(self) -> str:
        return constants.PROVIDER_NAME

    album_id: int

    async def save_track(self, track_id: int, connection: Connection):
        cursor = connection.execute((
            'update tracks '
            'set yc_track_id = ? '
            'where id = ? '
            'returning 1'
        ), (self.id, track_id))
        row = cursor.fetchone()
        if not row:
            _logger.warning(
                'Ошибка во время сохранения трека Яндекс музыки с id: %i для трека %i. Обновлено 0 записей',
                self.id, track_id
            )

    def create_track_source(self) -> TrackSource:
        return TrackSource(
            name=self.provider_name,
            url=create_track_source_url(self.album_id, self.id)
        )
