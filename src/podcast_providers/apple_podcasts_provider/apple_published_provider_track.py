from dataclasses import dataclass
from sqlite3 import Connection

from models.published_provider_track import PublishedProviderTrack
from models.track_source import TrackSource
from podcast_providers.apple_podcasts_provider import utils


@dataclass
class ApplePublishedProviderTrack(PublishedProviderTrack):
    podcast_id: str

    async def try_find_linked_saved_track_id(self, connection: Connection) -> int | None:
        found = connection.execute((
            'select id '
            'from tracks '
            'where ap_track_id = ?'
        ), (self.id,)).fetchone()
        if found:
            return found[0]

    @property
    def provider_name(self) -> str:
        return utils.PROVIDER_NAME

    async def save_track(self, track_id: int, connection: Connection):
        cursor = connection.cursor()
        try:
            cursor.execute((
                'update tracks '
                'set ap_track_id = ? '
                'where id = ?'
            ), (self.id, track_id))
        finally:
            cursor.close()

    def create_track_source(self) -> TrackSource:
        return TrackSource(
            name=utils.PROVIDER_NAME,
            url=utils.format_source_url(self.podcast_id, self.id)
        )

    async def check_saved(self, connection: Connection) -> bool:
        exists, = connection.execute((
            'select exists(select 1 from tracks where ap_track_id = ?)'
        ), (self.id,)).fetchone()
        return bool(exists)
