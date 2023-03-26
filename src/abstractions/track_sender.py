from abc import ABC, abstractmethod

from models.track import Track


class TrackSender(ABC):
    @abstractmethod
    async def send_track(self, track: Track):
        ...
