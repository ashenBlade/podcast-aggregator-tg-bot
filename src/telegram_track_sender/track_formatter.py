import html
import itertools
from datetime import datetime, timedelta

from aiogram.utils import markdown as fmt

from insfrastructure.utils import to_hashtag


def format_duration(duration: timedelta):
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds - hours * 3600) // 60)
    if hours:
        return f'{hours}ч {minutes}м'
    else:
        return f'{minutes}м'


def pre_process_description(description: str, max_length: int) -> str:
    paragraphs = description.strip().split('\n\n')
    if not paragraphs:
        return ''

    first_paragraph = paragraphs[0]
    return first_paragraph[:max_length] + ('...' if len(first_paragraph) > max_length else '')


def format_tags(tags: list[str], podcast_name: str):
    podcast_name_hashtag = to_hashtag(podcast_name)
    podcast_name_tuple = (podcast_name_hashtag,) if podcast_name_hashtag else tuple()
    return (
        f'#{tag}'
        for tag
        in itertools.chain(tags or tuple(), podcast_name_tuple)
    )


max_description_length = 500


def format_track_markdown(title: str, description: str, podcast: str, duration: timedelta | None, tags: list[str]):
    sections = [
        fmt.hbold(fmt.quote_html(title)),
        fmt.quote_html(pre_process_description(description, max_description_length))
    ]

    if duration:
        sections.append(f'Длительность: {format_duration(duration)}')

    sections.append(' '.join(format_tags(tags, podcast)))
    return '\n\n'.join(sections)
