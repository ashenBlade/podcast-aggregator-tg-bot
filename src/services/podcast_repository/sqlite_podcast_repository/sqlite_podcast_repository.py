import json
import sqlite3

from abstractions.podcast_repository import PodcastRepository
from models import Podcast
from services.podcast_providers import YandexMusicProvider


def parse_podcast_row(row: tuple):
    id, name, description, tags_str, yc_album = row
    providers = [YandexMusicProvider(yc_album)] if yc_album else []
    return Podcast(
        id=id,
        name=name,
        description=description,
        providers=providers,
        tags=json.loads(tags_str) if tags_str else None
    )


class SqlitePodcastRepository(PodcastRepository):
    database: str

    def __init__(self, database: str):
        self.database = database

    async def get_all_podcasts(self) -> list[Podcast]:
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute(
                'select p.id, p.name, p.description, ('
                ' case count(t.id) when 0 then null else json_group_array(t.tag) end'
                ') as tags, ymp.album '
                'from podcasts p '
                'left join podcast_tag pt on p.id = pt.podcast_id '
                'left join tags t on pt.tag_id = t.id '
                'left join yandex_music_providers ymp on p.id = ymp.podcast_id '
                'group by p.id, p.name, p.description;'
            )

            return [
                parse_podcast_row(row)
                for row
                in cursor.fetchall()
            ]
