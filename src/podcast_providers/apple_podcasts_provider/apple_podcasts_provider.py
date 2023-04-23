import logging
from dataclasses import dataclass
from datetime import date

import aiohttp

from models.podcast_provider import PodcastProvider
from models.published_provider_track import PublishedProviderTrack
from podcast_providers.apple_podcasts_provider import utils, parsing
from podcast_providers.apple_podcasts_provider.apple_published_provider_track import ApplePublishedProviderTrack

_logger = logging.getLogger(__name__)


@dataclass
class ApplePodcastsProvider(PodcastProvider):
    podcast_id: str

    @property
    def name(self) -> str:
        return utils.PROVIDER_NAME

    async def get_track_published_at(self, publish_date: date) -> PublishedProviderTrack | None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(utils.format_load_podcast_page_url(self.podcast_id)) as response:
                    body = await response.text()
                    for track in parsing.parse_published_tracks_ordered(body):
                        if track.publish_date == publish_date:
                            return ApplePublishedProviderTrack(
                                id=track.id,
                                provider=self,
                                publish_date=publish_date,
                                duration=track.duration,
                                description=track.description,
                                title=track.title,
                                source_url=utils.format_source_url(self.podcast_id, track.id),
                                podcast_id=self.podcast_id
                            )
                        if track.publish_date < publish_date:
                            return
        except aiohttp.ClientError as client_error:
            _logger.error('Ошибка во время запроса к серверам Apple', exc_info=client_error)


