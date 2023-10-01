from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.podcast import Podcast
    from models.published_provider_track import PublishedProviderTrack
    from models.track_source import TrackSource


@dataclass
class PublishedTrack:
    """
    Объект, представляющий агрегацию опубликованных треков провайдеров -
    создается на основании нескольких опубликованных
    """
    title: str
    description: str
    duration: timedelta
    podcast: 'Podcast'
    provider_tracks: list['PublishedProviderTrack']

    # Рудимент - раньше хотел для каждого добавить тэги (backend, analytics, lifestyle и т.д.),
    # но остановился на одном названии.
    tags: list[str]

    @property
    def sources(self) -> list['TrackSource']:
        return [
            pt.create_track_source()
            for pt
            in self.provider_tracks
        ]


