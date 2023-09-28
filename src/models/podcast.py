from dataclasses import dataclass
from datetime import date, timedelta

from models.podcast_provider import PodcastProvider
from models.published_provider_track import PublishedProviderTrack

from models.published_track import PublishedTrack


def format_description(description: str, min_description_length: int):
    sections = [
        section.strip()
        for section
        in description.split('\n\n')
    ]
    filtered = []

    for section in sections:
        filtered.append(section)
        min_description_length -= len(section)
        if min_description_length <= 0:
            break

    return '\n\n'.join(filtered)


DEFAULT_MIN_DESCRIPTION_LENGTH = 200


def get_result_description(tracks: list[PublishedProviderTrack]):
    """
    Отформатировать результирующее описание трека.
    :param tracks: Треки подкаста
    :return: Отформатированное описание подкаста
    """
    # Описание создается как описание с самым длинным текстом,
    # но при этом его обрезают до максимального значения
    return format_description(max((t.description for t in tracks), key=len), DEFAULT_MIN_DESCRIPTION_LENGTH)


def get_result_duration(provider_tracks):
    """
    Получить длительность подкаста
    :param provider_tracks: Треки провайдеров
    :return: Длительность трека
    """

    # Длительность формируется как
    # среднее арифметическое всех длительностей

    total_durations = [
        t.duration
        for t in provider_tracks
        if t.duration is not None
    ]

    if not total_durations:
        return None

    avg_seconds = (
        sum(d.total_seconds() for d in total_durations)
        /
        len(total_durations)
    )
    return timedelta(seconds=avg_seconds)


def get_result_title(provider_tracks):
    """
    Получить название трека подкаста
    :param provider_tracks: Треки провайдеров подкаста
    :return: Название трека
    """

    # Формируется как самое большое название из всех.
    # Его обрезать не рекомендуется (думаю, не надо)

    longest_title = max((
        t.title for t in provider_tracks
    ), key=len)
    return longest_title


@dataclass
class Podcast:
    """
    Объект подкаста.
    Представляется названием и ID из БД.
    Настоящая работа ведется через провайдеров подкастов.
    """

    id: int
    name: str
    providers: list[PodcastProvider]

    async def get_track_published_at(self, publish_date: date) -> PublishedTrack | None:
        """
        Получить трек, опубликованный в указанную дату
        :param publish_date: Дата публикации трека
        :return: Опубликованный трек, если есть, иначе None
        """

        # Поочереди получаем треки у каждого провайдера
        provider_tracks: list[PublishedProviderTrack] = [
            t
            for t
            in [
                await p.get_track_published_at(publish_date)
                for p
                in self.providers
            ] if t
        ]

        if not provider_tracks:
            return

        # Если найден, то форматируем его содержимое (агрегируем)

        description = get_result_description(provider_tracks)
        duration = get_result_duration(provider_tracks)
        title = get_result_title(provider_tracks)

        return PublishedTrack(
            provider_tracks=provider_tracks,
            description=description,
            duration=duration,
            title=title,
            podcast=self,
            tags=[]
        )

