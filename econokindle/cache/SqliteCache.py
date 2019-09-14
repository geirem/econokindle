from sqlite3 import Connection
from typing import Optional, Any

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
    #
    # def has(self, url: str) -> bool:
    #     key = self._key_creator.key(url)
    #     c = self.__connection.cursor()
    #     c.execute('SELECT 1 FROM Images WHERE id = ?', [key])
    #     results = c.fetchall()
    #     c.close()
    #     return len(results) == 1

    def get(self, url: str) -> Optional[str]:
        key = self._key_creator.key(url)
        c = self.__connection.cursor()
        if self._is_image(url):
            c.execute('SELECT content FROM Images WHERE id = ?', [key])
        else:
            c.execute('SELECT content FROM Documents WHERE id = ?', [key])
        results = c.fetchall()
        c.close()
        if len(results) == 0:
            return None
        result = results[0][0]
        return result

    def store(self, url: str, contents: Any) -> None:
        key = self._key_creator.key(url)
        c = self.__connection.cursor()
        if self._is_image(url):
            c.execute('INSERT INTO Images (id, url, content) VALUES (?, ?, ?)', [key, url, contents])
        else:
            c.execute('INSERT INTO Documents (id, url, content) VALUES (?, ?, ?)', [key, url, contents])
        self.__connection.commit()
        c.close()
