import os.path
from typing import Optional, Any
import os


class Cache:

    def __init__(self, path: str):
        if not path.endswith('/'):
            path += '/'
        self.__path = path
        if not os.path.exists(path):
            os.makedirs(path)

    def has(self, key: str) -> bool:
        if not key.startswith('.'):
            key = self.__key(key)
        return os.path.isfile(key)

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
                    data = contents.read(1024)
                    if not data:
                        break
                    out.write(data)
        else:
            with open(key, 'w') as writer:
                writer.write(contents)

    @staticmethod
    def __is_image(key: str) -> bool:
        return key.endswith('.png') or key.endswith('.jpg') or key.endswith('.gif')
