"""PryvateSQL tests."""
# pylint: disable=too-many-public-methods
import unittest

from pryvate.db import PryvateSQLite


class PryvateSQLiteTestCase(unittest.TestCase):

    """Seperate test case for the PryvateSQLite class."""

    def setUp(self):
        """Set up step for all tests."""
        self.pryvate_db = PryvateSQLite(':memory:')

    def tearDown(self):
        """Tear down step, clean up after yourself."""
        self.pryvate_db.connection.close()

    def test_get_eggs(self):
        """Test getting all eggs."""
        expected = []
        result = self.pryvate_db.get_eggs()
        assert result == expected

    def test_new_egg(self):
        """Test creating a new egg."""
        expected = True
        result = self.pryvate_db.new_egg('Foo')
        assert result == expected
        expected = {'name': 'Foo'}
        result = self.pryvate_db.connection.execute(self.pryvate_db.GET_ALL)
        for item in result:
            assert dict(item) == expected
