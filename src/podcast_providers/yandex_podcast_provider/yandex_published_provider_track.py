from dataclasses import dataclass
from sqlite3 import Connection

from models.published_provider_track import PublishedProviderTrack
from models.track_source import TrackSource
from podcast_providers.yandex_podcast_provider import constants


@dataclass
class YandexPublishedProviderTrack(PublishedProviderTrack):
    async def check_saved(self, connection: Connection) -> bool:
        exists, = connection.execute((
            'select exists(select 1 from tracks where yc_track_id = ?)'
        ), (self.id,)).fetchone()
        return exists

    @property
    def provider_name(self) -> str:
        return constants.PROVIDER_NAME

    def create_track_source(self) -> TrackSource:
        return TrackSource(
            url=self.source_url,
            name=constants.PROVIDER_NAME
        )

    async def save_track(self, track_id: int, connection: Connection):
        connection.execute((
            'update tracks '
            'set yc_track_id = ? '
            'where id = ? '
        ), (self.id, track_id))

    async def try_find_linked_saved_track_id(self, connection: Connection) -> int | None:
        cursor = connection.execute((
            'select id '
            'from tracks '
            'where yc_track_id = ?'
        ), (self.id,))
        row = cursor.fetchone()
        if not row:
            return None

        saved_track_id, = row
        return saved_track_id