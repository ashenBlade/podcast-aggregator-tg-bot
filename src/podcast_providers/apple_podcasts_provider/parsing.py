from urllib.parse import urlparse, parse_qs
from datetime import datetime
from typing import Generator

import dateparser
from bs4 import Tag, BeautifulSoup

from podcast_providers.apple_podcasts_provider.parsed_published_track import ParsedPublishedTrack


def parse_title(tag: Tag):
    # Похоже, что возвращаемый ответ не сжимается,
    # Поэтому надо убрать окаймляющие пустые строки
    return tag.h2.text.strip()


def parse_publish_date(tag: Tag):
    time_tag = tag.time
    try:
        return datetime.fromisoformat(time_tag.attrs['datetime']).date()
    except (ValueError, KeyError):
        return dateparser.parse(time_tag.text)


def parse_track_id(tag: Tag):
    anchor = tag.a
    try:
        return int(anchor.attrs['data-episode-id'])
    except (KeyError, TypeError):
        url = urlparse(anchor.attrs['href'])
        query_string = parse_qs(url.query)
        return int(query_string['i'])


def parse_description(tag: Tag):
    _, description_tag = tag.select('p')
    return description_tag.text.strip()


relative_time = datetime.now()
relative_time_settings = {'RELATIVE_BASE': relative_time}


def parse_duration(tag: Tag):
    for meta_tag in tag.select('.tracks__track__meta'):
        try:
            parsed = dateparser.parse(meta_tag.text.strip(), settings=relative_time_settings)
            if parsed:
                return relative_time - parsed
        except (TypeError, ValueError):
            pass


def try_parse_published_track_tag(tag: Tag) -> ParsedPublishedTrack | None:
    try:
        return ParsedPublishedTrack(
            duration=parse_duration(tag),
            description=parse_description(tag),
            publish_date=parse_publish_date(tag),
            title=parse_title(tag),
            id=parse_track_id(tag)
        )
    except:
        return None


def parse_published_tracks_ordered(body: str):
    soup = BeautifulSoup(body, features='lxml')
    track_tags = soup.select('.tracks > li')
    for tag in track_tags:
        parsed = try_parse_published_track_tag(tag)
        if parsed:
            yield parsed
