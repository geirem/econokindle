from typing import List

from econokindle.Cookie import Cookie


class CookieJar:

    def __init__(self):
        self.__cookies = []

    def add(self, cookie: Cookie) -> None:
        self.__cookies.append(cookie)

    def get_for_url(self, url: str) -> List[Cookie]:
        return [c for c in self.__cookies if c.applies_to(url)]
