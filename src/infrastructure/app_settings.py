from dataclasses import dataclass
from datetime import timedelta


@dataclass
class AppSettings:
    poll_interval: timedelta
    chat_id: int
    token: str
    database_file: str
    seed_podcasts_yaml_file: str | None
