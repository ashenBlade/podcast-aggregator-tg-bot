from dataclasses import dataclass
from datetime import date, timedelta

from models.podcast_provider import PodcastProvider
from models.published_provider_track import PublishedProviderTrack

from models.published_track import PublishedTrack


def get_result_description(tracks: list[PublishedProviderTrack]):
    longest_description = max((t.description for t in tracks), key=len)
    return longest_description


def get_result_duration(provider_tracks):
    total_durations = [
        t.duration
        for t in provider_tracks
        if t.duration is not None
    ]

    if not total_durations:
        return None

    avg_seconds = (
        sum(d.total_seconds() for d in total_durations)
        /
        len(total_durations)
    )
    return timedelta(seconds=avg_seconds)


def get_result_title(provider_tracks):
    longest_title = max((
        t.title for t in provider_tracks
    ), key=len)
    return longest_title


@dataclass
class Podcast:
    id: int
    name: str
    providers: list[PodcastProvider]
    tags: list[str]

    async def get_track_published_at(self, publish_date: date) -> PublishedTrack | None:
        provider_tracks: list[PublishedProviderTrack] = [
            t
            for t
            in [
                await p.get_track_published_at(publish_date)
                for p
                in self.providers
            ] if t
        ]

        if not provider_tracks:
            return

        description = get_result_description(provider_tracks)
        duration = get_result_duration(provider_tracks)
        title = get_result_title(provider_tracks)

        return PublishedTrack(
            provider_tracks=provider_tracks,
            description=description,
            duration=duration,
            title=title,
            podcast=self,
            tags=self.tags
        )

