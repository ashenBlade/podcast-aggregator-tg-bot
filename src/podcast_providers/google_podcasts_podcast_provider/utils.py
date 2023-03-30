PROVIDER_NAME = 'Google Подкасты'


def create_load_album_url(feed: str):
    return f'https://podcasts.google.com/feed/{feed}'


def create_track_source_url(feed: str, episode: str):
    return f'https://podcasts.google.com/feed/{feed}/episode/{episode}'
