from dataclasses import dataclass
from sqlite3 import Connection

from models.provider_track import ProviderTrack
from models.track_source import TrackSource
from podcast_providers.apple_podcasts_provider import utils


@dataclass
class AppleProviderTrack(ProviderTrack):
    podcast_id: str

    @property
    def provider_name(self) -> str:
        return utils.PROVIDER_NAME

    async def save_track(self, track_id: int, connection: Connection):
        connection.execute((
            'update tracks '
            'set ap_track_id = ? '
            'where id = ? '
        ), (self.id, track_id))

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
