from datetime import datetime, timedelta

from models import Track


def format_duration(duration: timedelta):
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds - hours * 3600) // 60)
    return f'{hours}ч{minutes}м'


def format_sources(track: Track):
    return '\n'.join(
        f'[{source.provider.name}]({source.url})'
        for source
        in track.sources
    )


def format_tags(track: Track):
    if not track.tags:
        return None

    return ' '.join(
        f'#{tag}'
        for tag
        in track.tags
    )


def format_track_markdown(track: Track):
    return (
        f'*{track.name}*\n'
        f'{track.description}\n\n'
        f'Длительность: {format_duration(track.duration)}\n'
        f'{format_sources(track)}\n'
        f'{format_tags(track)}'
    )