import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from abstractions.track_sender import TrackSender
from models import Track
from services.track_sender.telegram_track_sender.track_formatter import format_track_markdown


_logger = logging.getLogger(__file__)


def create_reply_source_url_keyboard(track: Track):
    if not track.sources:
        return
    keyboard = InlineKeyboardMarkup(row_width=1)
    for button in [
        InlineKeyboardButton(
            text=source.provider.name,
            url=source.url
        )
        for source in track.sources
    ]:
        keyboard.add(button)
    return keyboard


class TelegramTrackSender(TrackSender):
    bot: Bot

    def __init__(self, token: str, chat_id: int):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_track(self, track: Track):
        formatted_message = format_track_markdown(track)
        keyboard = create_reply_source_url_keyboard(track)
        try:
            await self.bot.send_message(
                self.chat_id,
                formatted_message,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        except Exception as e:
            _logger.error('Ошибка во время отправки сообщения в чат %i', self.chat_id, exc_info=e)
