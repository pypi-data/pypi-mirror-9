# -*- encoding: utf-8 -*-

from setuptools import find_packages, setup

from eveapi2 import VERSION

setup(
    name='eveapi2',
    version=VERSION,
    author=u'Lukas Nemec',
    author_email='lu.nemec@gmail.com',
    url='https://github.com/lunemec/eveapi2',
    license='see LICENSE.txt',
    description='Sane EVE Online API',
    long_description='''https://github.com/lunemec/eveapi2''',
    install_requires=[
        'beautifulsoup4',
        'pytz',
    ],
    setup_requires=[
        'beautifulsoup4',
        'pytz',
    ],
    provides=find_packages(),
    platforms='any',
    packages=find_packages(),
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Games/Entertainment',
    ]
)
