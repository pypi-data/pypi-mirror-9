"""Pryvate tests."""
# pylint: disable=too-many-public-methods
# pylint: disable=no-member

import os
import unittest
import shutil
import tempfile

from bs4 import BeautifulSoup

import pryvate


class PryvateTestCase(unittest.TestCase):

    """Main test case for Pryvate."""

    @staticmethod
    def _copy_egg(tempdir):
        """Copy the files from res/meep to {tempdir}/meep."""
        base = 'tests/res/meep'
        os.mkdir(os.path.join(tempdir, 'meep'))
        for item in os.listdir(base):
            shutil.copyfile(
                os.path.join(base, item),
                os.path.join(tempdir, 'meep', item),
            )

    def setUp(self):
        """Set up step for all tests."""
        self.egg_folder = tempfile.TemporaryDirectory()
        self._copy_egg(self.egg_folder.name)
        pryvate.server.app.config['BASEDIR'] = self.egg_folder.name
        pryvate.server.app.config['PRIVATE_EGGS'] = {'meep'}
        self.app = pryvate.server.app.test_client()
        self.simple = '/simple'
        self.pypi = '/pypi'
        self.packages = '/packages'

    def tearDown(self):
        """Tear down stop for all tests."""
        self.egg_folder.cleanup()

    def test_packages(self):
        """Assert that pryvate will send you a package."""
        expected = 'gzip'
        url = '{}/sdist/m/meep/meep-1.0.0.tar.gz'
        request = self.app.get(url.format(self.packages))
        assert expected in request.headers['Content-Type']
        assert request.status_code == 200

    def test_packages_cheeseshop(self):
        """Assert that pryvate will proxy unknown packages to cheeseshop."""
        expected = pryvate.server.app.config['PYPI'].format(
            '/packages/sdist/F/Flask/Flask-0.10.tar.gz',
        )
        url = '{}/sdist/F/Flask/Flask-0.10.tar.gz'
        request = self.app.get(url.format(self.packages))
        assert request.headers['Location'] == expected
        assert request.status_code == 301

    def test_pypi_register(self):
        """Assert that you can register a package with pryvate."""
        expected = b'ok'
        payload = {'name': 'foo', ':action': 'submit'}
        request = self.app.post(self.pypi, data=payload)
        assert expected == request.data
        assert request.status_code == 200
        assert 'foo' in os.listdir(self.egg_folder.name)
        assert 'foo' in pryvate.server.app.config['PRIVATE_EGGS']

    def test_pypi_upload(self):
        """Assert that you can upload a package with pryvate."""
        payload = {'name': 'foo', ':action': 'submit'}
        request = self.app.post(self.pypi, data=payload)

        filename = 'foo-1.0.0.tar.gz'
        filepath = os.path.join('tests/res', filename)
        expected = b'ok'
        payload = {'name': 'foo', ':action': 'file_upload',
                   'md5_digest': '80ce9a2b000eee531db2479fd16a5f38',
                   'content': (open(filepath, 'rb'), filename)}
        request = self.app.post(self.pypi, data=payload,
                                content_type='multipart/form-data')
        assert request.data == expected
        assert request.status_code == 200

    def test_simple_search(self):
        """Assert that the search feature is not implemented."""
        request = self.app.post(self.simple)
        assert request.status_code == 501
        assert request.data == b'Not implemented'

    def test_simple_get_all(self):
        """Assert that pryvate can return a list of packages."""
        expected = 'meep'
        request = self.app.get(self.simple)
        response = BeautifulSoup(request.data)
        assert request.status_code == 200
        assert expected in [a.string for a in response.find_all('a')]

    def test_simple_get_cheeseshop(self):
        """Assert that pryvate will proxy an unknown egg to the cheeseshop."""
        expected = 'Flask-0.10.tar.gz'
        request = self.app.get('{}/flask/'.format(self.simple))
        response = BeautifulSoup(request.data)
        assert request.status_code == 200
        assert expected in [a.string for a in response.find_all('a')]

    def test_simple_get_private_egg(self):
        """Assert that pryvate will return a privately registered egg."""
        expected = 'meep-1.0.0.tar.gz'
        request = self.app.get('{}/meep/'.format(self.simple))
        response = BeautifulSoup(request.data)
        assert request.status_code == 200
        assert expected in [a.string for a in response.find_all('a')]
