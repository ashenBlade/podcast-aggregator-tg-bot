import itertools
from datetime import datetime, timedelta


def format_duration(duration: timedelta):
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds - hours * 3600) // 60)
    return f'{hours}ч{minutes}м'


def format_tags(tags: list[str], podcast: str):
    podcast_name_tag = podcast.replace(' ', '')
    tags = tags or tuple()
    return ' '.join(
        f'#{tag}'
        for tag
        in itertools.chain(tags, (podcast_name_tag,))
    )


def format_track_markdown(title: str, description: str, podcast: str, duration: timedelta, tags: list[str]):
    return (
        f'*{title}*\n'
        f'{description}\n\n'
        f'Длительность: {format_duration(duration)}\n'
        f'{format_tags(tags, podcast)}\n'
    )
