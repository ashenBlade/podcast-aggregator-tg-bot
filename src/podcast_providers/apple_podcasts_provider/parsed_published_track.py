from dataclasses import dataclass
from datetime import timedelta, datetime, date


@dataclass
class ParsedPublishedTrack:
    id: str
    title: str
    description: str
    duration: timedelta | None
    publish_date: date
