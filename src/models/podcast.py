from dataclasses import dataclass, field
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
    tags: list[str] | None = None

    async def get_track_created_in_specified_day(self, published_date: date) -> Track | None:
        all_tracks: list[tuple[Track, PodcastProvider]] = []
        for provider in self.providers:
            track = await provider.get_track_published_in_specified_date(published_date)
            if track:
                all_tracks.append((track, provider))

        if not any(all_tracks):
            return None

        track_sources = [
            TrackSource(
                provider=provider,
                url=track.source_url
            )
            for (track, provider)
            in all_tracks
        ]

        average_duration_seconds = sum(
            t.duration.total_seconds()
            for (t, _)
            in all_tracks
        ) / len(all_tracks)

        first_description = next(
            (x.description for (x, _) in all_tracks if x.description),
            ''
        )

        first_name = next(
            (x.name for (x, _) in all_tracks if x.name),
            ''
        )

        return Track(
            name=first_name,
            duration=timedelta(seconds=average_duration_seconds),
            description=first_description,
            sources=track_sources,
            publication_date=published_date,
            tags=self.tags
        )
