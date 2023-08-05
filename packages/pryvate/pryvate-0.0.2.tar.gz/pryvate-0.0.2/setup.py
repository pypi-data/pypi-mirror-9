"""Setup file for handling the Pryvate package."""

from setuptools import find_packages, setup

setup(
    name='pryvate',
    description='Private PyPi proxy and repository',
    packages=find_packages(),
    version=open('VERSION', 'r').read().strip(),
    install_requires=[
        'Flask>=0.10,<1',
        'python-magic>=0.4,<1',
        'requests>=2.5,<3',
    ],
    entry_points={
        'console_scripts': [
            'pryvate-server = pryvate.server:run'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    zip_safe=False,
)
