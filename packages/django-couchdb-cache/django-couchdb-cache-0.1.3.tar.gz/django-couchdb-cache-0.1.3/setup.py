import os
from setuptools import setup

PACKAGE_VERSION = '0.1.3'
PACKAGE_NAME = 'django-couchdb-cache'

EXAMPLES_TARGET_DIR = 'share/{}/'.format(PACKAGE_NAME)
EXAMPLES_LOCAL_DIR = 'examples'


def get_data_files():
    data_files = [(os.path.join(EXAMPLES_TARGET_DIR, root), [os.path.join(root, f) for f in files]) for root, dirs, files in os.walk(EXAMPLES_LOCAL_DIR)]
    return data_files

setup(
    name=PACKAGE_NAME,
    author='ShuttleCloud Corp',
    author_email='dev@shuttlecloud.com',
    description='CouchDB cache application for Django',
    url='https://github.com/shuttlecloud/django-couchdb-cache.git',
    version=PACKAGE_VERSION,
    packages=['couchdb_cache'],
    include_package_data=True,
    zip_safe=False,
    scripts=[],
    data_files=get_data_files(),
    install_requires=[
        'Django<=1.7.4',
        'CouchDB==0.10',
        'python-memcached'
    ],
    dependency_links=[
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
    ]
)
