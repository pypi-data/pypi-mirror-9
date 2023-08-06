from distutils.core import setup
from pip.req import parse_requirements

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
    version='0.5.6',
    author="Gabriel Melillo",
    author_email="gabriel@melillo.me",
    maintainer="Gabriel Melillo",
    maintainer_email="gabriel@melillo.me",
    description="netxt-episode.net watch list unofficial api",
    url="https://github.com/gmelillo/next-episode-wl",
    install_requires=[ str(ir.req) for ir in parse_requirements('requirements.txt')],
    classifiers=CLASSIFIERS,
    platforms=['OS Independent'],
    data_files=[
        ('', ['requirements.txt'])
    ],
    include_package_data=True,
    packages=[
        'nextepisode',
    ],
    license="GNU GENERAL PUBLIC LICENSE",
    long_description='Class created to provide a easy access to your next episode watch '
                     'list and easy integrate information with tvrage'
)