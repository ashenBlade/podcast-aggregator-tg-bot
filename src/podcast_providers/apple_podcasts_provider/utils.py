PROVIDER_NAME = 'Apple Подкасты'


def format_load_podcast_page_url(podcast_id: str):
    """
    Создать строку для получения страницы подкаста
    :param podcast_id: ID Apple подкаста
    :return: строка URL
    """
    return f'https://podcasts.apple.com/ru/podcast/{podcast_id}'


def format_source_url(podcast_id: str, track_id: int):
    """
    Создать строку для перехода к треку на сайте Apple Подкастов
    :param podcast_id: ID подкаста
    :param track_id: ID эпизода подкаста
    :return: URL эпизода подкаста
    """
    return f'https://podcasts.apple.com/ru/podcast/{podcast_id}?i={track_id}'
