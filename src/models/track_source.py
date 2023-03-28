from dataclasses import dataclass


@dataclass
class TrackSource:
    name: str
    url: str

    def __eq__(self, other):
        return self.url.lower() == other.name.lower()

    def __hash__(self):
        return hash(self.name)
