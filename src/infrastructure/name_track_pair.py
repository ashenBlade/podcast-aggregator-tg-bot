from dataclasses import dataclass

from models.provider_track import ProviderTrack


@dataclass
class NameTrackPair:
    """
    Специальный тип, который используется для получения результирующего списка источников треков,
    когда трек уже был опубликован
    """
    track: ProviderTrack

    @property
    def name(self):
        return self.track.provider_name

    def __init__(self, track: ProviderTrack):
        self.track = track

    # Переопределяем магические методы, чтобы работал set

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, NameTrackPair) and other.name == self.name

    def __ge__(self, other):
        return self.name >= other.name

    def __lt__(self, other):
        return self.name < other.name
