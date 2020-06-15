import re
from typing import List

from urllib3 import HTTPResponse

from econokindle.Cookie import Cookie


class CookieJar:

    def __init__(self):
        self.__cookies = []

    def _add(self, cookie: Cookie) -> None:
        self.__cookies.append(cookie)

    def get_for_url(self, url: str) -> List[str]:
        return [c.get_for_header() for c in self.__cookies if c.applies_to(url)]

    def load_cookies(self, response: HTTPResponse) -> None:
        cookie_string = response.headers.get('set-cookie')
        if cookie_string is None:
            return
        # NOSONAR pythonsecurity:S2631
        parts = cookie_string.split(', ')
        new_cookies = []
        for p in parts:
            if re.search('^[^ ]+=', p):
                new_cookies.append(p)
            else:
                new_cookies[-1] += ', ' + p
        for new_cookie in new_cookies:
            self._add(Cookie(new_cookie.strip()))
