from abc import ABC, abstractmethod
from typing import Optional, Any

from econokindle import KeyCreator


class Cache(ABC):

    def __init__(self, key_creator: KeyCreator):
        self._key_creator = key_creator

    @abstractmethod
    def get(self, document: str) -> Optional[str]:
        pass

    @abstractmethod
    def store(self, document: str, contents: Any) -> None:
        pass

    @staticmethod
    def _is_image(key: str) -> bool:
        return key.split('.').pop() in ['png', 'jpg', 'gif']
