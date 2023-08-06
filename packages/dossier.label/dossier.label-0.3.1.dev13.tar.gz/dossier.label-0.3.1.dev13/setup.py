#!/usr/bin/env python

import os

from setuptools import setup, find_packages

from version import get_git_version
VERSION, SOURCE_LABEL = get_git_version()
PROJECT = 'dossier.label'
AUTHOR = 'Diffeo, Inc.'
AUTHOR_EMAIL = 'support@diffeo.com'
URL = 'http://github.com/dossier/dossier.label'
DESC = 'Label (ground truth) storage for DossierStack'


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
    license='MIT',
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
        'cbor',
        'enum34',
        'kvlayer',
        'pyquchk',
        'pytest',
        'yakonfig >= 0.7.2',
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'dossier.label = dossier.label.run:main',
        ],
    },
)
