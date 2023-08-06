from distutils.core import setup
from pip.req import parse_requirements
from nextepisode import __version__ as ne_version

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: End Users/Desktop',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
]


setup(
    name='NextEpisode',
    version=ne_version,
    author="Gabriel Melillo",
    author_email="gabriel@melillo.me",
    description="netxt-episode.net watch list unofficial api",
    url="https://github.com/gmelillo/next-episode-wl",
    install_requires=[ str(ir.req) for ir in parse_requirements('requirements.txt')],
    classifiers=CLASSIFIERS,
    platforms=['OS Independent'],
    packages=[
        'nextepisode',
    ],
    license="GNU GENERAL PUBLIC LICENSE",
    long_description='Class created to provide a easy access to your next episode watch '
                     'list and easy integrate information with tvrage'
)