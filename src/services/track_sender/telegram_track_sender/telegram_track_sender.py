import logging

from aiogram import Bot

from abstractions.track_sender import TrackSender
from models import Track
from services.track_sender.telegram_track_sender.track_formatter import format_track_markdown


_logger = logging.getLogger(__file__)


class TelegramTrackSender(TrackSender):
    bot: Bot

    def __init__(self, token: str, chat_id: int):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_track(self, track: Track):
        formatted_message = format_track_markdown(track)
        try:
            await self.bot.send_message(self.chat_id, formatted_message, parse_mode='Markdown')
        except Exception as e:
            _logger.error('Ошибка во время отправки сообщения в чат %i', self.chat_id, exc_info=e)
