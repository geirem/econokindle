import os
import os.path
import time
from typing import Optional, Any

from econokindle import KeyCreator


class Cache:

    BUFFER_SIZE = 1024 * 256

    def __init__(self, path: str, key_creator: KeyCreator):
        if not os.path.exists(path):
            os.makedirs(path)
        if not path.endswith('/'):
            path += '/'
        self.__path = path
        self.__now = time.time()
        self.__key_creator = key_creator

    def has(self, key: str) -> bool:
        if not key.startswith('.'):
            key = self.__key(key)
        if not os.path.isfile(key):
            return False
        file_info = os.stat(key)
        if file_info.st_size == 0:
            return False
        return True

    def __key(self, document: str) -> str:
        return self.__path + self.__key_creator.key(document)

    def get(self, document: str) -> Optional[str]:
        key = self.__key(document)
        if not self.has(key):
            return None
        data = ''
        with open(key, 'r', encoding='utf-8') as fp:
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
            with open(key, 'w', encoding='utf-8') as writer:
                writer.write(contents)

    @staticmethod
    def __is_image(key: str) -> bool:
        return key.endswith('.png') or key.endswith('.jpg') or key.endswith('.gif')
