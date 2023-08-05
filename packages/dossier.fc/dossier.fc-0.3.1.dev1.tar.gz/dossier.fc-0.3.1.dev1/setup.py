#!/usr/bin/env python

import os

from setuptools import setup, find_packages

from version import get_git_version
VERSION, SOURCE_LABEL = get_git_version()
PROJECT = 'dossier.fc'
AUTHOR = 'Diffeo, Inc.'
AUTHOR_EMAIL = 'support@diffeo.com'
URL = 'http://github.com/dossier/dossier.fc'
DESC = 'Feature collections for DossierStack'


def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()

setup(
    name=PROJECT,
    version=VERSION,
    description=DESC,
    license='MIT/X11 license http://opensource.org/licenses/MIT',
    long_description=read_file('README.md'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=find_packages(),
    namespace_packages=['dossier'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'cbor >= 0.1.13',
        'streamcorpus >= 0.3.27',
    ],
    extras_require={
        'unittest': [
            'pytest',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'dossier.fc = dossier.fc.dump:main',
            'dossier.fc.test = dossier.fc.tests.run:main',
        ],
    },
)
