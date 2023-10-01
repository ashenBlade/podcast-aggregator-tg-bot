from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.provider_track import ProviderTrack


@dataclass
class SavedTrack:
    """
    Трек подкаста, сохраненный в БД
    """
    id: int
    tg_message_id: int
    saved_provider_tracks: list['ProviderTrack']

    @property
    def sources(self):
        return [
            spt.create_track_source()
            for spt
            in self.saved_provider_tracks
        ]
