from dataclasses import dataclass


@dataclass
class TrackSource:
    """
    Пара (провайдер, адрес трека).
    Используется для передачи списка источников в телеграм сообщение (внизу ссылки которые)
    """
    name: str
    url: str

    def __eq__(self, other):
        return self.url.lower() == other.name.lower()

    def __hash__(self):
        return hash(self.name)
