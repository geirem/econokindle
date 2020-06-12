import re
import time
from typing import Any

from urllib3 import PoolManager, HTTPResponse
from urllib3.exceptions import MaxRetryError

from econokindle.Cookie import Cookie
from econokindle.CookieJar import CookieJar
from econokindle.Cache import Cache
from econokindle.KeyCreator import KeyCreator
from econokindle.exceptions.RetrievalError import RetrievalError


class Fetcher:

    def __init__(self, pool_manager: PoolManager, key_creator: KeyCreator, cache: Cache):
        self.__pool_manager = pool_manager
        self.__cache = cache
        self.__cookie_jar = CookieJar()

    def fetch_page(self, url: str) -> str:
        cached = self.__cache.get(url)
        if cached is not None:
            return cached
        return self.__fetch_uncached(url)

    def __update_cookies(self, response: HTTPResponse) -> None:
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
            self.__cookie_jar.add(Cookie(new_cookie.strip()))

    def __fetch_uncached(self, url: str) -> str:
        while True:
            try:
                response = self.__execute_request(url)
                contents = response.data.decode("utf-8")
                if 'preloadedData' in contents or '__NEXT_DATA__' in contents:
                    self.__cache.store(url, contents)
                    return contents
            except (MaxRetryError, RetrievalError):
                pass
            else:
                print('.', end='')
                time.sleep(10)

    def __cookies_as_header(self, url: str) -> str:
        return '; '.join(self.__cookie_jar.get_for_url(url))

    def __execute_request(self, url: str, preload_content=True) -> Any:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
        }
        cookies = self.__cookies_as_header(url)
        if cookies != "":
            headers['Cookie'] = cookies
        response = self.__pool_manager.request("GET", url, headers=headers, preload_content=preload_content)
        self.__update_cookies(response)
        status = response.status
        if status != 200:
            raise RetrievalError()
        return response

    def fetch_image(self, url: str) -> bytes:
        image = self.__cache.get(url)
        if not image:
            image = self.__execute_request(url, False).read()
            self.__cache.store(url, image)
        return image
