from setuptools import setup

__version__ = '0.0.1'

import os

def _read(name):
    try: return open(os.path.join(os.path.dirname(__file__), name)).read()
    except: return ''

_short_description = '`itako` is a package for development at Itako Inc.'
_readme = _read('README')
_changes = _read('CHANGES')
_license = _read('LICENSE')

_long_description = _readme + '\n' + _changes

setup(
    name='itako',
    version=__version__,
    description=_short_description,
    long_description=_long_description,
    url='https://github.com/Itakoh/itako-py',
    author='Ike Tohru',
    author_email='ike.tohru@gmail.com',
    license='BSD',
    packages=['itako'],
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'itako=itako.command:console',
        ],
    },
    test_suite="itako",
)
