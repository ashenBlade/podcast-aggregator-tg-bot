import datetime
import json
import logging
import sqlite3
from datetime import datetime, date

from models.podcast import Podcast
from models.provider_track import ProviderTrack
from models.published_track import PublishedTrack
from models.saved_track import SavedTrack
from podcast_providers import YandexMusicProvider
from podcast_providers.yandex_podcast_provider.yandex_provider_track import YandexProviderTrack

_logger = logging.getLogger(__name__)


def parse_podcast_row(row: tuple):
    id, name, tags_str, yc_album_id = row
    providers = [YandexMusicProvider(album=yc_album_id)] if yc_album_id else []
    return Podcast(
        id=id,
        name=name,
        providers=providers,
        tags=json.loads(tags_str) if tags_str else []
    )


class SqlitePodcastManager:
    database: str

    def __init__(self, database: str):
        self.database = database

    async def get_all_podcasts(self) -> list[Podcast]:
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute(
                'select p.id, p.name, ('
                ' case count(t.id) when 0 then null else json_group_array(t.tag) end'
                ') as tags, p.yc_album_id '
                'from podcasts p '
                'left join podcast_tag pt on p.id = pt.podcast_id '
                'left join tags t on pt.tag_id = t.id '
                'group by p.id, p.name, p.yc_album_id;'
            )

            return [
                parse_podcast_row(row)
                for row
                in cursor.fetchall()
            ]

    async def save_new_track(self,
                             tg_message_id: int,
                             podcast_id: int,
                             publish_date: datetime,
                             provider_tracks: list[ProviderTrack]):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            cursor.execute('begin')
            try:
                track_id, = cursor.execute((
                    'insert into tracks(podcast_id, tg_message_id, publish_date) '
                    'values (?, ?, ?) '
                    'returning id'
                ), (podcast_id, tg_message_id, publish_date)).fetchone()

                for t in provider_tracks:
                    await t.save_track(track_id, cursor)

                cursor.execute('commit')
                return track_id
            except:
                cursor.execute('rollback')

    async def try_find_saved_track(self, track: PublishedTrack) -> SavedTrack | None:
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            for pt in track.provider_tracks:
                found_id = await pt.try_find_linked_saved_track_id(cursor)
                if not found_id:
                    continue

                row = cursor.execute((
                    'select t.id, t.podcast_id, t.tg_message_id, t.yc_track_id '
                    'from tracks t '
                    'where t.id = ? '
                ), (found_id,)).fetchone()
                if not row:
                    _logger.warning('Провайдер %s вернул ID несуществующего трека', pt.provider.name)
                    continue

                track_id, podcast_id, tg_message_id, yc_track_id = row
                saved_provider_tracks = []
                if yc_track_id:
                    album_id = cursor.execute((
                        'select yc_album_id '
                        'from podcasts '
                        'where id = ?'
                    ), (podcast_id,)).fetchone()
                    saved_provider_tracks.append(YandexProviderTrack(
                        id=yc_track_id,
                        album_id=album_id
                    ))

                return SavedTrack(
                    id=track_id,
                    tg_message_id=tg_message_id,
                    saved_provider_tracks=saved_provider_tracks
                )

    async def update_tracks(self, track_id: int, provider_tracks: list[ProviderTrack]):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            cursor.execute('begin')
            try:
                for pt in provider_tracks:
                    if not await pt.check_saved(cursor):
                        await pt.save_track(track_id, cursor)
                cursor.execute('commit')
            except Exception as e:
                cursor.execute('rollback')
                raise e

    async def all_provider_track_saved(self, provider_tracks: list[ProviderTrack]):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            for pt in provider_tracks:
                if not await pt.check_saved(cursor):
                    return False

            return True
