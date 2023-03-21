from abc import ABC, abstractmethod

from models import Track


class TrackSender(ABC):
    @abstractmethod
    async def send_track(self, track: Track):
        ...
