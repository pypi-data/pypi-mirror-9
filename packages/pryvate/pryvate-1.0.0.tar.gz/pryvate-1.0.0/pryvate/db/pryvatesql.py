"""Pryvate database: SQLite."""
import sqlite3


class PryvateSQLite(object):

    """Use SQLite to save egg information.

    Attempts to create the ``eggs`` table if
    it does not already exist.

    Keyword Arguments:
        name (``str``, optional): Path to the database
            *Default:* ``pryvate.db``
    """

    CREATE = 'CREATE TABLE IF NOT EXISTS eggs (name TEXT);'
    GET_ALL = 'SELECT name FROM eggs;'
    NEW_EGG = 'INSERT INTO eggs (name) VALUES (?);'

    def __init__(self, name='pryvate.db'):
        """Initialize a new database connection."""
        self.connection = sqlite3.connect(name)
        self.connection.execute(self.CREATE)
        self.connection.commit()
        self.connection.row_factory = sqlite3.Row

    def get_eggs(self):
        """Get available private eggs.

        Returns:
            ``list`` of ``str``
        """
        rows = self.connection.execute(self.GET_ALL)
        return [item['name'] for item in rows]

    def new_egg(self, name):
        """Add new egg to list.

        Arguments:
            name (``str``): The name of the egg to add

        Returns:
            ``bool``
        """
        row_count = self.connection.execute(self.NEW_EGG, (name, )).rowcount
        self.connection.commit()
        return bool(row_count)
