__author__ = 'Gabriel Melillo<gabriel@melillo.me>'
__version__ = '0.1'

from sqlite3 import connect
from os import path
from json import dumps, loads


class TVRageCache(object):
    DEFAULT_CACHE_FILE = 'tvrage.cache'

    def __init__(self, **kwargs):
        self._cache_file = kwargs.get('cachefile', self.DEFAULT_CACHE_FILE)
        self._cursor = None
        self._db = None
        self._connected = False

        if kwargs.get('autoconnect', True):
            self.connect()

    def connect(self):
        if not path.isfile(self._cache_file):
            self._db = connect(self._cache_file)
            self._cursor = self._db.cursor()
            self._cursor.execute('''
                CREATE TABLE IF NOT EXISTS tvrage(
                    uuid TEXT unique,
                    json TEXT,
                    creation NUMERIC,
                    expire NUMERIC
                )
            ''')
            self._db.commit()
        else:
            self._db = connect(self._cache_file)
            self._cursor = self._db.cursor()

    def _clear_expired(self):
        self._cursor.execute('''DELETE FROM tvrage WHERE expire <= date('now')''')
        self._db.commit()

    def write_cache(self, uuid, data, expire):
        self._cursor.execute('INSERT OR REPLACE INTO tvrage VALUES (?,?,date(),?)', (
            uuid,
            dumps(data),
            expire
        ))
        self._db.commit()
        self._clear_expired()

    def get_cache(self, uuid):
        self._cursor.execute('SELECT * FROM tvrage WHERE uuid=?', (uuid,))
        data = self._cursor.fetchone()
        self._clear_expired()
        if data is not None:
            return loads(data[1])
        else:
            return None