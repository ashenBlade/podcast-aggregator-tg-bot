from sqlite3 import Connection

from models.published_provider_track import PublishedProviderTrack
from models.track_source import TrackSource
from podcast_providers.google_podcasts_podcast_provider import utils


class GooglePublishedProviderTrack(PublishedProviderTrack):
    @property
    def provider_name(self) -> str:
        return utils.PROVIDER_NAME

    async def try_find_linked_saved_track_id(self, connection: Connection) -> int | None:
        raise NotImplementedError

    async def save_track(self, track_id: int, connection: Connection):
        raise NotImplementedError

    def create_track_source(self) -> TrackSource:
        raise NotImplementedError

    async def check_saved(self, connection: Connection) -> bool:
        raise NotImplementedError
