import asyncio
import datetime
import logging
import os
from datetime import timedelta, datetime

from insfrastructure.app_settings import AppSettings
from services.podcast_repository.sqlite_podcast_repository.sqlite_podcast_repository import SqlitePodcastRepository
from services.track_sender.telegram_track_sender.telegram_track_sender import TelegramTrackSender


def get_app_settings():
    hours = int(os.environ['POLL_INTERVAL_HOURS'])
    poll_interval = timedelta(hours=hours)
    token = os.environ['BOT_TOKEN']
    chat_id = int(os.environ['CHAT_ID'])
    db_file = os.environ['DB_FILE']

    return AppSettings(
        poll_interval=poll_interval,
        token=token,
        chat_id=chat_id,
        database_file=db_file
    )


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


async def main():
    settings = get_app_settings()
    _logger = logging.getLogger(__name__)
    podcast_repository = SqlitePodcastRepository(
        database=settings.database_file
    )
    sender = TelegramTrackSender(
        token=settings.token,
        chat_id=settings.chat_id,
    )
    _logger.info('Работа приложения начинается')
    while True:
        try:
            podcasts = await podcast_repository.get_all_podcasts()
            _logger.debug('Загружено %i подкастов из БД', len(podcasts))
            today = datetime.today().date()
            tracks = [
                track for track in [
                    await podcast.get_track_created_in_specified_day(today)
                    for podcast
                    in podcasts
                ] if track and not await podcast_repository.is_track_already_sent(track)
            ]
            _logger.debug('Обнаружено %i новых треков подкастов', len(tracks))
            if tracks:
                for track in tracks:
                    await sender.send_track(track)
                    await podcast_repository.mark_track_sent(track)

        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            _logger.info('Запрошено завершение работы во время обработки подкастов', exc_info=e)
            break
        except Exception as e:
            _logger.error('Ошибка во время работы сервера', exc_info=e)

        try:
            sleep_delay_seconds = settings.poll_interval.total_seconds()
            _logger.debug('Засыпаю на %.1f минут после отправки треков', sleep_delay_seconds / 60)
            await asyncio.sleep(sleep_delay_seconds)
        except (KeyboardInterrupt, asyncio.CancelledError) as e:
            _logger.info('Завершение работы приложения', exc_info=e)
            break

if __name__ == '__main__':
    asyncio.run(main())
