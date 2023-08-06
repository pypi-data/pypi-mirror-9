"""Pryvate server."""
import os

from flask import Flask, g

from pryvate.blueprints.packages import packages
from pryvate.blueprints.pypi import pypi
from pryvate.blueprints.simple import simple
from pryvate.defaultconfig import DefaultConfig
from pryvate.db import PryvateSQLite

app = Flask(__name__)
app.config.from_object(DefaultConfig)
if os.environ.get('PRYVATE_CONFIG'):
    app.config.from_envvar('PRYVATE_CONFIG')
else:
    app.logger.warning('env var PRYVATE_CONFIG not set, running with defaults')

if not os.path.isdir(app.config['BASEDIR']):
    os.mkdir(app.config['BASEDIR'])


app.register_blueprint(packages.blueprint)
app.register_blueprint(pypi.blueprint)
app.register_blueprint(simple.blueprint)


@app.before_request
def before_request():
    """Start a database connection."""
    g.database = PryvateSQLite(app.config['DB_PATH'])


@app.teardown_request
def teardown_request(_):
    """Close the database connection if it exists."""
    database = getattr(g, 'database', None)
    if database is not None:
        database.connection.close()


def run(host=None, debug=False):
    """Start the server.

    This function is only available for
    the console script exposed by installing
    the pryvate package.

    Keyword Arguments:
        host (``str``, optional): The interface the server will bind to
            *Default:* ``None``
        debug (``bool``, optional): Start the Flask server in debug mode
            *Default:* ``False``
    """
    app.run(host=host, debug=debug)


if __name__ == '__main__':
    run(host='0.0.0.0', debug=True)
