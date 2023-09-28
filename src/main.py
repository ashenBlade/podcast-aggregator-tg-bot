import asyncio
import datetime
import logging
import os
from datetime import timedelta, datetime

from infrastructure.app_settings import AppSettings
from infrastructure.name_track_pair import NameTrackPair
from models.provider_track import ProviderTrack
from models.published_track import PublishedTrack
from sqlite_podcast_manager.sqlite_podcast_manager import SqlitePodcastManager
from telegram_track_sender.telegram_track_sender import TelegramTrackSender
from infrastructure.yaml_podcasts_loader import load_podcasts_info


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
_logger = logging.getLogger(__name__)


def get_app_settings():
    try:
        hours = int(os.environ['POLL_INTERVAL_HOURS'])
    except KeyError:
        _logger.info("Значение интервала обновления не указано. Выставляю %i часов", 1)
        hours = 1

    if hours < 1:
        raise ValueError('Интервал работы должен быть положительным. Передано %i', hours)

    poll_interval = timedelta(hours=hours)

    try:
        token = os.environ['BOT_TOKEN']
    except KeyError:
        token = None

    if not token:
        raise ValueError('В BOT_TOKEN не указан токен бота')

    try:
        chat_id = int(os.environ['CHAT_ID'])
    except (KeyError, ValueError):
        raise ValueError('Не удалось получить ID чата из переменной CHAT_ID')

    yaml_file = os.environ.get('SEED_PODCASTS_FILE', None)

    default_database_file = 'podcasts.sqlite'

    database_file = os.environ.get('DB_FILE', None)
    if not database_file:
        _logger.info('Файл базы данных не указан. Использую %s', default_database_file)
        database_file = default_database_file

    return AppSettings(
        poll_interval=poll_interval,
        token=token,
        chat_id=chat_id,
        database_file=database_file,
        seed_podcasts_yaml_file=yaml_file
    )


async def poll_for_tracks(sender: TelegramTrackSender, podcast_manager: SqlitePodcastManager):
    try:
        podcasts = await podcast_manager.get_all_podcasts()
        _logger.debug('Загружено %i подкастов из БД', len(podcasts))
        today = datetime.today().date()
        published_tracks: list[PublishedTrack] = [
            track for track in [
                await podcast.get_track_published_at(today)
                for podcast
                in podcasts
            ] if track
        ]
        if not published_tracks:
            _logger.info('Новых треков не обнаружено')
            return

        _logger.info('Обнаружено %i новых треков подкастов', len(published_tracks))

        for published_track in published_tracks:
            _logger.info('Обрабатываю эпизод "%s"', published_track.title)
            saved_track = await podcast_manager.try_find_saved_track(published_track)
            if saved_track:
                _logger.debug('Трек уже был сохранен. Id = %i', saved_track.id)
                result_provider_tracks: list[ProviderTrack] = [
                    x.track
                    for x
                    in sorted({
                        *(NameTrackPair(track=spt) for spt in saved_track.saved_provider_tracks),
                        *(NameTrackPair(track=pt) for pt in published_track.provider_tracks)
                    })
                ]

                if await podcast_manager.all_provider_track_saved(result_provider_tracks):
                    _logger.debug('Для эпизода %i не нашлось новых треков от других провайдеров', saved_track.id)
                    continue

                _logger.info('Для трека %i найдено %i треков провайдеров', saved_track.id, len(result_provider_tracks))

                result_track_sources = [
                    pt.create_track_source()
                    for pt
                    in result_provider_tracks
                ]

                try:
                    await sender.update_track_sources(saved_track.tg_message_id, result_track_sources)
                    _logger.info('Кнопки для трека %i обновлены', saved_track.id)
                except Exception as e:
                    _logger.error('Ошибка во время обновления кнопок ссылок для сообщения %i трека %i в телеграмме',
                                  saved_track.tg_message_id, saved_track.id, exc_info=e)
                    continue
                try:
                    await podcast_manager.update_tracks(saved_track.id, result_provider_tracks)
                    _logger.info('Трек %i обновлен', saved_track.id)
                except Exception as e:
                    _logger.error('Ошибка во время обновления БД для трека %i', saved_track.id, exc_info=e)
                    continue
            else:  # Полностью новый
                try:
                    message_id = await sender.send_track(
                        published_track.title,
                        published_track.description,
                        published_track.podcast.name,
                        published_track.duration,
                        published_track.sources,
                        published_track.tags
                    )
                    _logger.info('Трек %s отправлен в телеграмм. Присвоен ID сообщения %i',
                                 published_track.title, message_id)
                except Exception as e:
                    _logger.error('Ошибка во время отправки трека %s', published_track, exc_info=e)
                    continue

                try:
                    track_id = await podcast_manager.save_new_track(
                        message_id,
                        published_track.podcast.id,
                        datetime.now(),
                        provider_tracks=published_track.provider_tracks
                    )
                    _logger.info('Трек %s сохранен. Присвоен Id %i', published_track.title, track_id)
                except Exception as e:
                    _logger.error('Ошибка во время сохранения трека %s', published_track, exc_info=e)

    except (KeyboardInterrupt, asyncio.CancelledError) as e:
        raise e
    except Exception as e:
        _logger.error('Ошибка во время работы сервера', exc_info=e)


async def main():
    try:
        settings = get_app_settings()
    except ValueError as ve:
        _logger.critical('Ошибка при получении конфигурации', exc_info=ve)
        return

    podcast_manager = SqlitePodcastManager(
        database=settings.database_file
    )
    sender = TelegramTrackSender(
        token=settings.token,
        chat_id=settings.chat_id,
    )

    podcast_manager.create_database()

    if settings.seed_podcasts_yaml_file:
        _logger.info("Открываю %s файл для загрузки подкастов", settings.seed_podcasts_yaml_file)
        try:
            with open(settings.seed_podcasts_yaml_file) as seed_file:
                podcasts = load_podcasts_info(seed_file)
                podcast_manager.seed_database(podcasts)
        except FileNotFoundError as fnfe:
            _logger.warning('Файл %s не найден', exc_info=fnfe)

    _logger.info('Работа приложения начинается')
    while True:
        try:
            await poll_for_tracks(sender, podcast_manager)

            sleep_delay_seconds = settings.poll_interval.total_seconds()
            _logger.debug('Засыпаю на %.1f минут после отправки треков', sleep_delay_seconds / 60)
            await asyncio.sleep(sleep_delay_seconds)
        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            _logger.info('Завершение работы приложения', exc_info=e)
            break

if __name__ == '__main__':
    asyncio.run(main())
