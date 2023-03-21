from dataclasses import dataclass
from datetime import timedelta, datetime


@dataclass
class ProviderTrack:
    id: int
    name: str
    description: str
    tags: str
    publication_date: datetime
    duration: timedelta
    source_url: str

