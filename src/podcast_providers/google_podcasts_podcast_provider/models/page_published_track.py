from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any


@dataclass
class PagePublishedTrack:
    episode_id: str
    title: str
    description: str
    publish_date: date
    duration: timedelta
