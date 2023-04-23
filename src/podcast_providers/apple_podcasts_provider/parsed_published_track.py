from dataclasses import dataclass
from datetime import timedelta, date


@dataclass
class ParsedPublishedTrack:
    id: str
    title: str
    description: str
    duration: timedelta | None
    publish_date: date
