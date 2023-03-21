from dataclasses import dataclass

from models.podcast_provider import PodcastProvider


@dataclass
class TrackSource:
    provider: PodcastProvider
    url: str
