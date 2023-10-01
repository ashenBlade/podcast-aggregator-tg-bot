import logging
from datetime import timedelta

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from models.track_source import TrackSource
from telegram_track_sender.track_formatter import format_track_markdown


_logger = logging.getLogger(__name__)


def create_reply_source_url_keyboard(sources: list[TrackSource]):
    if not sources:
        return
    keyboard = InlineKeyboardMarkup(row_width=1)
    for button in [
        InlineKeyboardButton(
            text=source.name,
            url=source.url
        )
        for source in sources
    ]:
        keyboard.add(button)
    return keyboard


class TelegramTrackSender:
    bot: Bot

    def __init__(self, token: str, chat_id: int):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_track(self,
                         title: str,
                         description: str,
                         podcast: str,
                         duration: timedelta,
                         track_sources: list[TrackSource],
                         tags: list[str]):
        """
        Отправить новое сообщение и вернуть его ID
        :param title: Заголовок трека
        :param description: Описание трека
        :param podcast: Название подкаста
        :param duration: Длительность трека
        :param track_sources: Источники, где можно послушать
        :param tags: Тэги трека/подкаста
        :return: ID отправленного сообщения
        """

        formatted_message = format_track_markdown(title, description, podcast, duration, tags)
        keyboard = create_reply_source_url_keyboard(track_sources)
        message = await self.bot.send_message(
            self.chat_id,
            formatted_message,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        return message.message_id

    async def update_track_sources(self, message_id: int, track_sources: list[TrackSource]):
        """
        Обновить источники трека, у существующего сообщения.
        Все источники заменяются полностью!

        :param message_id: ID сообщения
        :param track_sources: Источники трека
        """
        keyboard = create_reply_source_url_keyboard(track_sources)
        await self.bot.edit_message_reply_markup(
            chat_id=self.chat_id,
            message_id=message_id,
            reply_markup=keyboard
        )
