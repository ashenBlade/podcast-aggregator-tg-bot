from sqlite3 import Connection

from models.provider_track import ProviderTrack
from models.track_source import TrackSource
from podcast_providers.google_podcasts_podcast_provider import utils


class GoogleProviderTrack(ProviderTrack):
    @property
    def provider_name(self) -> str:
        return utils.PROVIDER_NAME

    async def save_track(self, episode_id: int, connection: Connection):
        raise NotImplementedError

    def create_track_source(self) -> TrackSource:
        raise NotImplementedError

    async def check_saved(self, connection: Connection) -> bool:
        raise NotImplementedError
