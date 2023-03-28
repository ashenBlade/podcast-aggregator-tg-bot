from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.podcast import Podcast
    from models.published_provider_track import PublishedProviderTrack
    from models.track_source import TrackSource


@dataclass
class PublishedTrack:
    title: str
    description: str
    duration: timedelta
    podcast: 'Podcast'
    provider_tracks: list['PublishedProviderTrack']
    tags: list[str]

    @property
    def sources(self) -> list['TrackSource']:
        return [
            pt.create_track_source()
            for pt
            in self.provider_tracks
        ]


