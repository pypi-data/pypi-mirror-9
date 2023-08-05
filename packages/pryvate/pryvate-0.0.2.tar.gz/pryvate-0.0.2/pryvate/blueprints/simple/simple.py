"""Simple blueprint."""
import os

import requests
from flask import Blueprint, current_app, make_response, render_template

blueprint = Blueprint('simple', __name__, url_prefix='/simple',
                      template_folder='templates')


@blueprint.route('', methods=['POST'])
def search_simple():
    """Handling pip search.

    I don't fancy parsing XML payloads to be honest,
    if you cannot live without being able to search through
    pryvate you're welcome to create a pull request at
    https://github.com/dinoshauer/pryvate

    Returns:
        ``501`` - Not implemented
    """
    return make_response('Not implemented', 501)


@blueprint.route('', methods=['GET'])
def get_simple():
    """List all packages.

    Returns:
        A HTML page with a list of all the packages registered
        in pryvate
    """
    packages = os.listdir(current_app.config['BASEDIR'])
    return render_template('simple.html', packages=packages)


@blueprint.route('/<package>', methods=['GET'])
@blueprint.route('/<package>/', methods=['GET'])
def get_package(package):
    """List versions of a package.

    Returns:
        A HTML page with a list of all versions of a specific
        package registered in pryvate

        In case a given package is not registered in pryvate,
        the request is proxied to another CheeseShop
    """
    package_path = os.path.join(current_app.config['BASEDIR'],
                                package.lower())
    if package in current_app.config['PRIVATE_EGGS'] and os.path.isdir(package_path):
        files = os.listdir(package_path)
        packages = []
        for filename in files:
            if filename.endswith('md5'):
                digest_file = os.path.join(package_path, filename)
                with open(digest_file, 'r') as md5_digest:
                    item = {
                        'name': package,
                        'version': filename.replace('.md5', ''),
                        'digest': md5_digest.read()
                    }
                    packages.append(item)
        return render_template('simple_package.html', packages=packages,
                               letter=package[:1].lower())
    base_url = current_app.config['PYPI']
    url = base_url.format('/simple/{}/'.format(package.lower()))
    response = requests.get(url)
    return response.content, response.status_code
