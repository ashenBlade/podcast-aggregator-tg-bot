from datetime import datetime, timedelta, date

from pydantic import BaseModel, Field


class Track(BaseModel):
    id: int
    title: str
    publication_date: date = Field(alias='pubDate')
    duration_ms: int = Field(alias='durationMs')
    short_description: str = Field(alias='shortDescription', default='')

    @property
    def duration(self) -> timedelta:
        return timedelta(milliseconds=self.duration_ms)
