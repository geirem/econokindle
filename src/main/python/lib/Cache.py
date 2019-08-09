import os
import os.path
from typing import Optional, Any


class Cache:

    BUFFER_SIZE = 1024 * 256

    # TODO: age / now can be combined to the time stamp before which items are stale.
    def __init__(self, path: str, max_age: int, now: float):
        if not path.endswith('/'):
            path += '/'
        self.__path = path
        self.__max_age = max_age
        self.__now = now
        if not os.path.exists(path):
            os.makedirs(path)

    def has(self, key: str) -> bool:
        if not key.startswith('.'):
            key = self.__key(key)
        if not os.path.isfile(key):
            return False
        file_info = os.stat(key)
        if self.__now - file_info.st_mtime > self.__max_age:
            return False
        return True

    @staticmethod
    def __canonicalize_name(document: str) -> str:
        return document.split('/').pop()

    def __key(self, document: str) -> str:
        key = self.__path + self.__canonicalize_name(document)
        return key

    def get(self, document: str) -> Optional[str]:
        key = self.__key(document)
        if not self.has(key):
            return None
        data = ''
        with open(key, 'r') as fp:
            for line in fp:
                data += line.strip()
        return data

    def store(self, document: str, contents: Any) -> None:
        key = self.__key(document)
        if self.__is_image(document):
            with open(key, 'wb') as out:
                while True:
                    data = contents.read(self.BUFFER_SIZE)
                    if not data:
                        break
                    out.write(data)
        else:
            with open(key, 'w') as writer:
                writer.write(contents)

    @staticmethod
    def __is_image(key: str) -> bool:
        return key.endswith('.png') or key.endswith('.jpg') or key.endswith('.gif')
