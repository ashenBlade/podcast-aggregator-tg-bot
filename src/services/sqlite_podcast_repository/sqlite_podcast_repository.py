import sqlite3

from abstractions.podcast_repository import PodcastRepository
from models import Podcast
from services.podcast_providers import YandexMusicProvider


def parse_podcast_row(row: tuple):
    id, name, description, yc_album = row
    providers = [YandexMusicProvider(yc_album)] if yc_album else []
    return Podcast(
        id=id,
        name=name,
        description=description,
        providers=providers
    )


class SqlitePodcastRepository(PodcastRepository):
    database: str

    def __init__(self, database: str):
        self.database = database

    async def get_all_podcasts(self) -> list[Podcast]:
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute(
                'select id, name, description, ymp.album as yandex_music_album '
                'from podcasts '
                'left join yandex_music_providers ymp on podcasts.id = ymp.podcast_id'
            )

            return [
                parse_podcast_row(row)
                for row
                in cursor.fetchall()
            ]
