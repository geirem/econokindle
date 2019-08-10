import os
import os.path
import time
from typing import Optional, Any

from lib import KeyCreator


class Cache:

    BUFFER_SIZE = 1024 * 256

    # TODO: age / now can be combined to the time stamp before which items are stale.
    def __init__(self, path: str, max_age: int, key_creator: KeyCreator):
        if not os.path.exists(path):
            os.makedirs(path)
        if not path.endswith('/'):
            path += '/'
        self.__path = path
        self.__max_age = max_age
        self.__now = time.time()
        self.__key_creator = key_creator

    def has(self, key: str) -> bool:
        if not key.startswith('.'):
            key = self.__key(key)
        if not os.path.isfile(key):
            return False
        file_info = os.stat(key)
        if self.__now - file_info.st_mtime > self.__max_age:
            return False
        return True

    def __key(self, document: str) -> str:
        return self.__path + self.__key_creator.key(document)

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
