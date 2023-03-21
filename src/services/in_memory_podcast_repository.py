from abstractions.podcast_repository import PodcastRepository
from models import Podcast


class InMemoryPodcastRepository(PodcastRepository):
    podcasts: list[Podcast]

    def __init__(self, podcasts: list[Podcast]):
        self.podcasts = podcasts

    async def get_all_podcasts(self) -> list[Podcast]:
        return self.podcasts
