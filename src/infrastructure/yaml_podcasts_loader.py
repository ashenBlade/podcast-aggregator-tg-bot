import io

import pydantic
import yaml
from yaml import YAMLObject


class PodcastInfo(pydantic.BaseModel):
    name: str
    yandex: str | None
    google: str | None
    apple: str | None


def load_podcasts_info(stream: io.IOBase | str) -> list[PodcastInfo]:
    data = yaml.safe_load(stream)
    podcasts_yaml_array: list
    if 'podcasts' in data:
        podcasts_yaml_array = data['podcasts']
    else:
        podcasts_yaml_array = data

    podcasts = [
        PodcastInfo(**obj)
        for obj in podcasts_yaml_array
    ]
    return podcasts
