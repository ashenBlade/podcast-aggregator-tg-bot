import html
import itertools
from datetime import datetime, timedelta

import aiogram.utils.markdown
from aiogram.utils import markdown as fmt


def format_duration(duration: timedelta):
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds - hours * 3600) // 60)
    if hours:
        return f'{hours}ч {minutes}м'
    else:
        return f'{minutes}м'


def format_tags(tags: list[str], podcast: str):
    podcast_name_tag = podcast.replace(' ', '')
    tags = tags or tuple()
    return (
        f'#{tag}'
        for tag
        in itertools.chain(tags, (podcast_name_tag,))
    )


def format_track_markdown(title: str, description: str, podcast: str, duration: timedelta, tags: list[str]):
    return fmt.text(
        fmt.hbold(fmt.quote_html(title)), '\n\n',
        fmt.quote_html(description), '\n\n',
        'Длительность: ', format_duration(duration), '\n\n',
        fmt.text(*format_tags(tags, podcast)), '\n\n'
    )
