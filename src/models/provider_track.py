from dataclasses import dataclass
from datetime import timedelta, datetime

from models.provider_info import ProviderInfo


@dataclass
class ProviderTrack:
    id: int
    name: str
    description: str
    publication_date: datetime
    duration: timedelta
    source_url: str
    provider_info: ProviderInfo

