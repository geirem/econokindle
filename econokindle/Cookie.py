from urllib.parse import urlparse


class Cookie:

    def __init__(self, cookie):
        self.__raw_cookie = cookie
        self.__properties = {}
        parts = cookie.split(';')
        self.__name, self.__value = parts.pop(0).split('=', 1)
        for part in parts:
            if '=' not in part:
                continue
            key, value = part.strip().split('=', 1)
            self.__properties[key.lower()] = value

    def applies_to(self, url: str) -> bool:
        parsed = urlparse(url)
        if 'secure' in self.__properties and parsed.scheme != 'https':
            return False
        if 'path' in self.__properties and not parsed.path.starts_with(self.__properties['path']):
            return False
        return True

