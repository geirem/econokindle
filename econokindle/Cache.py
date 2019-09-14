from typing import Optional, Any

from econokindle import KeyCreator


class Cache:

    def __init__(self, key_creator: KeyCreator):
        self._key_creator = key_creator

    def get(self, document: str) -> Optional[str]:
        raise NotImplementedError

    def store(self, document: str, contents: Any) -> None:
        raise NotImplementedError

    @staticmethod
    def _is_image(key: str) -> bool:
        return key.split('.').pop() in ['png', 'jpg', 'gif']
