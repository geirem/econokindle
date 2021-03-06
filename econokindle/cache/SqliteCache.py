from sqlite3 import Connection
from typing import Optional, Any
import datetime

from econokindle.Cache import Cache
from econokindle import KeyCreator


class SqliteCache(Cache):

    def __init__(self, connection: Connection, key_creator: KeyCreator):
        super().__init__(key_creator)
        self.__connection = connection
        c = self.__connection.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Documents (
            id TEXT PRIMARY KEY,
            url TEXT,
            content TEXT,
            retrieved DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS Images (
            id TEXT PRIMARY KEY,
            url TEXT,
            content BLOB,
            retrieved DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        c.close()

    def get(self, url: str) -> Optional[str]:
        key = self._key_creator.key(url)
        c = self.__connection.cursor()
        if self._is_image(url):
            c.execute('SELECT content, retrieved FROM Images WHERE id = ?', [key])
        else:
            c.execute('SELECT content, retrieved FROM Documents WHERE id = ?', [key])
        results = c.fetchall()
        c.close()
        if len(results) == 0:
            return None
        retrieved = datetime.datetime.strptime(results[0][1], '%Y-%m-%d %H:%M:%S').timestamp()
        now = datetime.datetime.now().timestamp()
        if retrieved + 86400 < now:
            return None
        result = results[0][0]
        return result

    def store(self, url: str, contents: Any) -> None:
        key = self._key_creator.key(url)
        c = self.__connection.cursor()
        if self._is_image(url):
            c.execute('REPLACE INTO Images (id, url, content) VALUES (?, ?, ?)', [key, url, contents])
        else:
            c.execute('REPLACE INTO Documents (id, url, content) VALUES (?, ?, ?)', [key, url, contents])
        self.__connection.commit()
        c.close()
