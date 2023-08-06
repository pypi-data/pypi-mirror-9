"""PyPi blueprint."""
import os
from flask import Blueprint, current_app, g, request

blueprint = Blueprint('pypi', __name__, url_prefix='/pypi')


def register_package(localproxy):
    """Register a new package.

    Creates a folder on the filesystem so a new package can be uploaded.

    Arguments:
        localproxy (``werkzeug.local.LocalProxy``): The localproxy object is
            needed to read the ``form`` properties from the request

    Returns:
        ``'ok'``
    """
    package_dir = os.path.join(current_app.config['BASEDIR'],
                               localproxy.form['name'].lower())
    if not os.path.isdir(package_dir):
        os.mkdir(package_dir)
    return 'ok'


def upload_package(localproxy):
    """Save a new package and it's md5 sum in a previously registered path.

    Arguments:
        localproxy (``werkzeug.local.LocalProxy``):The localproxy object is
            needed to read the ``form`` properties from the request

    Returns:
        ``'ok'``
    """
    contents = localproxy.files['content']
    digest = localproxy.form['md5_digest']
    file_path = os.path.join(current_app.config['BASEDIR'],
                             localproxy.form['name'].lower(),
                             contents.filename.lower())

    contents.save(file_path)
    with open('{}.md5'.format(file_path), 'w') as md5_digest:
        md5_digest.write(digest)
    return 'ok'


@blueprint.route('', methods=['POST'])
def post_pypi():
    """Find a package and return the contents of it.

    Upon calling this endpoint the ``PRIVATE_EGGS`` set will be updated,
    and proper action will be taken based on the request.
    """
    actions = {
        'submit': register_package,
        'file_upload': upload_package,
    }
    if g.database.new_egg(request.form['name'].lower()):
        return actions[request.form[':action']](request)
