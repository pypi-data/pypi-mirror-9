"""Default Pryvate config."""


class DefaultConfig(object):

    """Class containing the default config for the Pryvate package.

    Anything can be overwritten! This is a regular old Flask configuration,
    read more here: http://flask.pocoo.org/docs/0.10/config/ and here
    http://flask.pocoo.org/docs/0.10/api/#flask.Flask.default_config

    The few options pryvate needs are:

    * ``BASEDIR`` - Where to store packages
    * ``PYPI`` - The url to the cheeseshop where public packages are stored
    * ``PRIVATE_EGGS`` - The names of private packages that pryvate intercepts
    """

    BASEDIR = './eggs/'
    PYPI = 'https://pypi.python.org{}'
    PRIVATE_EGGS = {}
