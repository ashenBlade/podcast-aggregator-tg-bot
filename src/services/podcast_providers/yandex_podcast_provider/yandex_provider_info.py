from dataclasses import dataclass

from models.provider_info import ProviderInfo


@dataclass
class YandexProviderInfo(ProviderInfo):
    """
    Id трека, указанный в Яндекс Музыке
    """
    id: int
