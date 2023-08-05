from os.path import join, dirname
from setuptools import setup as _setup


DIR = dirname(__file__)

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
]


def normalize_line(line):
    return line.split('#', 1)[0].strip()


def reqs(filename):
    with open(join(DIR, 'requirements', filename)) as f:
        return [l for l in map(normalize_line, f) if l]


def install_requires():
    return reqs('default.txt')


def get_kwargs():
    kwargs = {
        'author': 'Tomas Flam',
        'classifiers': classifiers,
        'description': 'Data Transfer Object library',
        'install_requires': install_requires(),
        'license': 'BSD',
        'name': 'DtoTools',
        'packages': ['dtotools'],
        'url': 'https://github.com/TomasFlam/python-dtotools',
        'version': '0.1.0.dev1',
    }
    return kwargs


def setup():
    _setup(**get_kwargs())


if __name__ == '__main__':
    setup()
