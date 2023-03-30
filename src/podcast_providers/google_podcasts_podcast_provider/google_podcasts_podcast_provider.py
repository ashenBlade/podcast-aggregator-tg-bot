from dataclasses import dataclass
from datetime import date

import aiohttp

from models.podcast_provider import PodcastProvider
from models.published_provider_track import PublishedProviderTrack
from podcast_providers.google_podcasts_podcast_provider import utils
from podcast_providers.google_podcasts_podcast_provider.google_published_provider_track import \
    GooglePublishedProviderTrack
from podcast_providers.google_podcasts_podcast_provider.parsing import parse_google_published_tracks_ordered


@dataclass
class GooglePodcastsPodcastProvider(PodcastProvider):
    feed: str

    @property
    def name(self) -> str:
        return utils.PROVIDER_NAME

    async def get_track_published_at(self, publish_date: date) -> PublishedProviderTrack | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(utils.create_load_album_url(self.feed)) as response:
                body = await response.text()
                for track in parse_google_published_tracks_ordered(body):
                    if track.publish_date == publish_date:
                        return GooglePublishedProviderTrack(
                            id=track.episode_id,
                            title=track.title,
                            publish_date=track.publish_date,
                            duration=track.duration,
                            description=track.description,
                            provider=self,
                            source_url=utils.create_track_source_url(self.feed, track.episode_id),
                            feed_id=self.feed
                        )
                    if track.publish_date < publish_date:
                        return
