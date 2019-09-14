from sqlite3 import Connection
from typing import Optional, Any

from econokindle.Cache import Cache
from econokindle import KeyCreator


class SqliteCache(Cache):

    def __init__(self, connection: Connection, key_creator: KeyCreator):
        super().__init__(key_creator)
        self.__connection = connection
        c = self.__connection.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS Documents (id TEXT PRIMARY KEY, url TEXT, content TEXT, retrieved DATETIME DEFAULT CURRENT_TIMESTAMP)')
        c.execute('CREATE TABLE IF NOT EXISTS Images (id TEXT PRIMARY KEY, url TEXT, content BLOB, retrieved DATETIME DEFAULT CURRENT_TIMESTAMP)')
        c.close()
    #
    # def foo(self):
    #     c = conn.cursor()
    #
    #     # Create table
    #
    #     # Insert a row of data
    #     c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
    #
    #     # Save (commit) the changes
    #     conn.commit()
    #
    #     # We can also close the connection if we are done with it.
    #     # Just be sure any changes have been committed or they will be lost.
    #     conn.close()
    #
    #     symbol = 'RHAT'
    #     c.execute("SELECT * FROM stocks WHERE symbol = '%s'" % symbol)
    #
    #     # Do this instead
    #     t = ('RHAT',)
    #     c.execute('SELECT * FROM stocks WHERE symbol=?', t)
    #     print c.fetchone()
    #
    #     # Larger example that inserts many records at a time
    #     purchases = [('2006-03-28', 'BUY', 'IBM', 1000, 45.00),
    #                  ('2006-04-05', 'BUY', 'MSFT', 1000, 72.00),
    #                  ('2006-04-06', 'SELL', 'IBM', 500, 53.00),
    #                  ]
    #     c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)

    def get(self, document: str) -> Optional[str]:
        key = self._key_creator.key(document)
        c = self.__connection.cursor()
        c.execute('SELECT content FROM Documents WHERE id = ?', [key])
        results = c.fetchall()
        a = 1
        return None

    def store(self, document: str, contents: Any) -> None:
        key = self._key_creator.key(document)
        c = self.__connection.cursor()
        if self._is_image(document):
            #     c.executemany('INSERT INTO stocks VALUES (?,?,?,?,?)', purchases)
            pass
        else:
            pass
