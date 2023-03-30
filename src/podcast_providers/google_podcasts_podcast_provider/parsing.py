import logging
import re
from datetime import datetime

import dateparser
from bs4 import BeautifulSoup, Tag

from podcast_providers.google_podcasts_podcast_provider.models.page_published_track import PagePublishedTrack

track_id_regex = re.compile(r'\./feed/\w+/episode/(\w+)\?.*')
relative_time = datetime.now()
relative_time_settings = {'RELATIVE_BASE': relative_time}


def _parse_track_id(tag: Tag):
    href = tag.attrs['href']
    return track_id_regex.findall(href)[0]


def _parse_duration(duration_tag: Tag):
    # В последнем тэге есть 2 div'а, причем текст в первом - сама длительность
    duration_text: str = duration_tag.div.text

    # Длительность некоторых не указана
    if not duration_text or duration_text.isspace():
        return None

    # Почему-то парсит время назад, а не вперед
    # Когда передается '1 hr 30 min' время откатывается назад, а не вперед, относительно relative_time
    parsed_date = dateparser.parse(duration_text, settings=relative_time_settings)

    # Может ли быть так?
    if parsed_date is None:
        return None

    return relative_time - parsed_date


def _extract_tags(top_level: Tag):
    divs = list(top_level.findNext('div').children)

    # Обычный вариант
    # При использовании только питона
    # Скорее всего будет использоваться этот вариант
    if len(divs) == 4:
        return divs

    # В каких-то местах может быть новая/пустая строка.
    # Получил такой вариант, когда делал запросы через Postman
    if len(divs) == 9:
        if divs[0].text.isspace():
            return divs[1::2]
        return divs[0::2]


def _parse_publish_date(publish_day_tag):
    # Неправильно парсит '1 day ago'
    text = publish_day_tag.text
    parsed_datetime = dateparser.parse(text)
    return parsed_datetime.date()


def _parse_description(description_tag: Tag):
    return description_tag.get_text(separator='\n')


def _parse_title(title_tag):
    return title_tag.text


_logger = logging.getLogger(__name__)


def _parse_track(tag: Tag) -> PagePublishedTrack:
    try:
        track_id = _parse_track_id(tag)

        # Все необходимые данные располагаются каждый в своем div'е именно в таком порядке
        publish_day_tag, title_tag, description_tag, duration_tag = list(tag.findNext('div').children)

        publish_date = _parse_publish_date(publish_day_tag)
        title = _parse_title(title_tag)
        description = _parse_description(description_tag)
        duration = _parse_duration(duration_tag)

        return PagePublishedTrack(
            episode_id=track_id,
            description=description,
            title=title,
            duration=duration,
            publish_date=publish_date
        )
    except Exception as e:
        _logger.warning('Ошибка во время парсинга трека гугл подкастов', exc_info=e)


def parse_google_published_tracks_ordered(body: str) -> list[PagePublishedTrack]:
    soup = BeautifulSoup(body, 'lxml')

    # Вроде div с такими параметрами на странице только один...
    newest_tracks_section = soup.find('div', {'role': 'list'})

    # Все эпизоды располагаются внутри якоря
    tags = newest_tracks_section.findAll('a')

    return (
        t for t in (
            _parse_track(tag)
            for tag
            in tags
        ) if t
    )
