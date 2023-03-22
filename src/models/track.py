from dataclasses import dataclass, field
from datetime import datetime, timedelta

from models.provider_info import ProviderInfo
from models.track_source import TrackSource


@dataclass
class Track:
    name: str
    description: str
    publication_date: datetime
    duration: timedelta
    sources: list[TrackSource]
    tags: list[str]
    provider_infos: list[ProviderInfo] = field(default_factory=list)
