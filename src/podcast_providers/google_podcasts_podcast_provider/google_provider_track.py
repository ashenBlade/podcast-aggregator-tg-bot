from dataclasses import dataclass
from sqlite3 import Connection

from models.provider_track import ProviderTrack
from models.track_source import TrackSource
from podcast_providers.google_podcasts_podcast_provider import utils


@dataclass
class GoogleProviderTrack(ProviderTrack):
    feed_id: str

    @property
    def provider_name(self) -> str:
        return utils.PROVIDER_NAME

    async def save_track(self, track_id: int, connection: Connection):
        connection.execute((
            'update tracks '
            'set gp_episode_id = ? '
            'where id = ?'
        ), (self.id, track_id))

    def create_track_source(self) -> TrackSource:
        return TrackSource(
            name=self.provider_name,
            url=utils.create_track_source_url(self.feed_id, self.id)
        )

    async def check_saved(self, connection: Connection) -> bool:
        exists, = connection.execute((
            'select exists(select 1 from tracks where gp_episode_id = ?)'
        ), (self.id,))
        return bool(exists)
