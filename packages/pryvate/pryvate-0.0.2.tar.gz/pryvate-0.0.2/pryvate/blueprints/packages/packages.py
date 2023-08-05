"""Package blueprint."""
import os

import magic
from flask import Blueprint, current_app, make_response, redirect, request

blueprint = Blueprint('packages', __name__, url_prefix='/packages')


@blueprint.route('/<_>/<__>/<name>/<filename>', methods=['GET'])
def packages(_, __, name, filename):
    """Get the contents of a package.

    The two first arguments are unused and specified as such by ``_``.

    Arguments:
        _ (``str``): *Unused* this is the package_type part of the /packages
            url, e.g.: ``sdist``/``source``
        __ (``str``): *Unused* this is the initial letter part of the /packages
            url, e.g.: ``F`` for ``Flask``
        name (``str``): This is the name of the package as defined in setup.py
        filename (``str``): This is the filename being requested, e.g.:
            ``Flask-0.10.0.tar.gz``

    Returns:
        Status codes:
        * ``200``
        * ``404``
        * ``301``
    """
    filepath = os.path.join(current_app.config['BASEDIR'], name.lower(),
                            filename.lower())

    if name in current_app.config['PRIVATE_EGGS']:
        if os.path.isfile(filepath):
            with open(filepath, 'rb') as egg:
                mimetype = magic.from_file(filepath, mime=True)
                contents = egg.read()
                return make_response(contents, 200, {'Content-Type': mimetype})
        return make_response('not found', 404)
    else:
        base_url = current_app.config['PYPI']
        url = base_url.format(request.path)
        return redirect(url, 301)
