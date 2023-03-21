from abstractions.track_sender import TrackSender
from models import Track


class ConsoleTrackSender(TrackSender):
    async def send_track(self, track: Track):
        print(f'Подкаст: {track.name}\n'
              f'Описание: {track.description}\n'
              f'Длительность: {track.duration}')
