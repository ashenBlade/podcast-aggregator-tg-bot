from dataclasses import dataclass
from datetime import date, timedelta

from models.podcast_provider import PodcastProvider
from models.track import Track
from models.track_source import TrackSource


@dataclass
class Podcast:
    id: int
    name: str
    description: str
    providers: list[PodcastProvider]

    async def get_track_created_in_specified_day(self, published_date: date) -> Track | None:
        all_tracks = [
            await provider.get_track_published_in_specified_date(published_date)
            for provider
            in self.providers
        ]

        if not any(all_tracks):
            return None

        track_sources = [
            TrackSource(
                provider=self,
                url=track.source_url
            )
            for track
            in all_tracks
        ]

        average_duration_seconds = sum(
            t.duration.total_seconds()
            for t
            in all_tracks
        ) / len(all_tracks)

        first_description = next(
            (x.description for x in all_tracks if x.description),
            ''
        )

        first_name = next(
            (x.name for x in all_tracks if x.name),
            ''
        )

        return Track(
            name=first_name,
            duration=timedelta(seconds=average_duration_seconds),
            description=first_description,
            sources=track_sources,
            publication_date=published_date,
        )
