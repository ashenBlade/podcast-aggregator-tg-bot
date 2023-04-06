from typing import Generator

from bs4 import Tag

from podcast_providers.apple_podcasts_provider.parsed_published_track import ParsedPublishedTrack


def try_parse_published_track_tag(tag: Tag) -> ParsedPublishedTrack | None:
    pass


def parse_published_tracks_ordered(body: str) -> Generator[ParsedPublishedTrack]:
    raise NotImplementedError


