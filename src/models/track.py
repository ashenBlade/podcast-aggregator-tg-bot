from dataclasses import dataclass
from datetime import datetime, timedelta

from models.track_source import TrackSource


@dataclass
class Track:
    name: str
    description: str
    publication_date: datetime
    duration: timedelta
    sources: list[TrackSource]
