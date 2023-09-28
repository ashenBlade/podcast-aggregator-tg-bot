import json
import logging
import sqlite3
from datetime import datetime

from models.podcast import Podcast
from models.provider_track import ProviderTrack
from models.published_track import PublishedTrack
from models.saved_track import SavedTrack
from podcast_providers import YandexMusicProvider
from podcast_providers.apple_podcasts_provider.apple_podcasts_provider import ApplePodcastsProvider
from podcast_providers.apple_podcasts_provider.apple_provider_track import AppleProviderTrack
from podcast_providers.google_podcasts_podcast_provider.google_podcasts_podcast_provider import \
    GooglePodcastsPodcastProvider
from podcast_providers.google_podcasts_podcast_provider.google_provider_track import GoogleProviderTrack
from podcast_providers.yandex_podcast_provider.yandex_provider_track import YandexProviderTrack

_logger = logging.getLogger(__name__)


def parse_podcast_row(row: tuple):
    id, name, tags_str, yc_album_id, gp_feed_id, ap_podcast_id = row
    providers = []
    if yc_album_id:
        providers.append(YandexMusicProvider(album=yc_album_id))

    if gp_feed_id:
        providers.append(GooglePodcastsPodcastProvider(feed=gp_feed_id))

    if ap_podcast_id:
        providers.append(ApplePodcastsProvider(podcast_id=ap_podcast_id))

    tags = json.loads(tags_str) if tags_str else []

    return Podcast(
        id=id,
        name=name,
        providers=providers,
        tags=tags
    )


class SqlitePodcastManager:
    database: str

    def __init__(self, database: str):
        self.database = database

    def create_database(self):
        """
        Инициализировать схему БД
        """
        cursor: sqlite3.Cursor
        with sqlite3.connect(self.database) as connection:
            with connection.cursor() as cursor:
                try:
                    _logger.info('Начинаю создание схемы БД')
                    cursor.executescript('''
begin;

create table podcasts(
    id integer primary key autoincrement,
    name varchar not null,
    yc_album_id integer,
    gp_feed_id varchar null,
    ap_podcast_id varchar
);

create unique index PODCASTS_YC_ALBUM_ID on podcasts(yc_album_id);
create unique index PODCASTS_GP_FEED_ID on podcasts(gp_feed_id);
create unique index PODCASTS_AP_PODCAST_ID on podcasts(ap_podcast_id);

create table tracks(
    id integer primary key autoincrement,
    podcast_id integer references podcasts(id) not null,
    tg_message_id integer not null,
    publish_date timestamp not null,
    yc_track_id integer,
    ap_track_id integer null,
    gp_episode_id varchar
);

create unique index TRACKS_TG_MESSAGE_ID on tracks(tg_message_id);
create unique index TRACKS_YC_TRACK_ID on tracks(yc_track_id);
create unique index TRACKS_GP_EPISODE_ID on tracks(gp_episode_id);
create unique index TRACKS_AP_TRACK_ID on tracks(ap_track_id);

commit;
''')
                    _logger.info("База данных инициализирована")
                except sqlite3.OperationalError as oe:
                    _logger.info("База данных уже инициализирована", exc_info=oe)

    async def get_all_podcasts(self) -> list[Podcast]:
        with sqlite3.connect(self.database) as connection:
            cursor = connection.execute(
                'select p.id, p.name, '
                '(case count(t.id) when 0 then null else json_group_array(t.tag) end) as tags, '
                'p.yc_album_id, p.gp_feed_id, p.ap_podcast_id '
                'from podcasts p '
                'left join podcast_tag pt on p.id = pt.podcast_id '
                'left join tags t on pt.tag_id = t.id '
                'group by p.id, p.name, p.yc_album_id, p.gp_feed_id, p.ap_podcast_id;'
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
                raise

    async def try_find_saved_track(self, track: PublishedTrack) -> SavedTrack | None:
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            for pt in track.provider_tracks:
                found_id = await pt.try_find_linked_saved_track_id(cursor)
                if not found_id:
                    continue

                row = cursor.execute((
                    'select t.id, t.podcast_id, t.tg_message_id, t.yc_track_id, t.gp_episode_id, t.ap_track_id '
                    'from tracks t '
                    'where t.id = ? '
                ), (found_id,)).fetchone()
                if not row:
                    _logger.warning('Провайдер %s вернул ID несуществующего трека', pt.provider.name)
                    continue

                track_id, podcast_id, tg_message_id, yc_track_id, gp_episode_id, ap_track_id = row
                saved_provider_tracks = []
                if yc_track_id:
                    album_id, = cursor.execute((
                        'select yc_album_id '
                        'from podcasts '
                        'where id = ?'
                    ), (podcast_id,)).fetchone()
                    saved_provider_tracks.append(YandexProviderTrack(
                        id=yc_track_id,
                        album_id=album_id
                    ))

                if gp_episode_id:
                    gp_feed_id, = cursor.execute((
                        'select gp_feed_id '
                        'from podcasts '
                        'where id = ?'
                    ), (podcast_id,)).fetchone()
                    saved_provider_tracks.append(GoogleProviderTrack(
                        id=gp_episode_id,
                        feed_id=gp_feed_id
                    ))

                if ap_track_id:
                    ap_podcast_id = cursor.execute((
                        'select ap_podcast_id '
                        'from podcasts '
                        'where id = ?'
                    ), (podcast_id,)).fetchone()
                    saved_provider_tracks.append(AppleProviderTrack(
                        id=ap_track_id,
                        podcast_id=ap_podcast_id
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

    def seed_database(self, podcasts):
        with sqlite3.connect(self.database) as connection:
            cursor = connection.cursor()
            for p in podcasts:
                try:
                    cursor.execute("""
                INSERT INTO podcasts(name, yc_album_id, gp_feed_id, ap_podcast_id)
                VALUES (?, ?, ?, ?) 
                """, (p.name, p.yandex, p.google, p.apple))
                except sqlite3.IntegrityError:
                    _logger.debug('Подкаст %s уже есть в БД', p.name)
