from typing import List

from econokindle import Cookie


class CookieJar:

    def __init__(self):
        self.__cookies = []

    def add(self, cookie: Cookie) -> None:
        self.__cookies.append(cookie)

    def get_for_url(self, url: str) -> List[Cookie]:
        return []
