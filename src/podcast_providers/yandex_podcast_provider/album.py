from datetime import date
from functools import cached_property

from pydantic import BaseModel, Field

from .track import Track


class Album(BaseModel):
    id: int
    title: str
    short_description: str = Field(alias='shortDescription')
    volumes: list[list[Track]]

    def get_track_published_in(self, publish_date: date) -> Track | None:
        for volume in self.volumes:
            for track in volume:
                if track.publication_date.date() == publish_date:
                    return track
        return None
