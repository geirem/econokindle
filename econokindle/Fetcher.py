import logging
import time
import os
from requests import Session

from econokindle.Cache import Cache
from econokindle.exceptions.RetrievalError import RetrievalError

_log = logging.getLogger(__name__)


class Fetcher:

    def __init__(self, session: Session, cache: Cache) -> None:
        self._session = session
        self._session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/83.0'
        self.__cache = cache

    def fetch_page(self, url: str) -> str:
        return self.__cache.get(url) or self.__fetch_uncached(url)

    def __fetch_uncached(self, url: str) -> str:
        while True:
            try:
                response = self._session.get(url)
                if response.status_code != 200:
                    continue
                if '__NEXT_DATA__' in response.text:
                    self.__cache.store(url, response.text)
                    return response.text
            except RetrievalError:
                pass
            else:
                print('.', end='')
                time.sleep(10)

    def fetch_image(self, url: str) -> bytes:
        image = self.__cache.get(url)
        if not image or len(image) < 1024:
            response = self._session.get(url)
            if response.status_code == 200:
                image = response.content
            else:
                _log.warning(f"Unable to fetch image {url}, using default.")
                fetcher_location = os.path.dirname(os.path.abspath(__file__))
                default_img_path = os.path.join(fetcher_location, "..", "resources", "default.png")
                with open(default_img_path, 'rb') as inimage:
                    image = inimage.read()
            self.__cache.store(url, image)
        return image
