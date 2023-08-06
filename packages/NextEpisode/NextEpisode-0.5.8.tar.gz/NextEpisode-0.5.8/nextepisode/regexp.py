__author__ = 'Gabriel Melillo<gabriel@melillo.me>'
__version__ = '0.1'

from re import search as reg_search


class Expression(object):
    SHOW_ID = "Show ID@([0-9]{0,5})\\n"
    SHOW_NAME = "Show Name@([a-zA-Z0-9_'\. ]*)\\n"
    URL = "Show URL@([a-zA-Z0-9_'\. /:-]*)\\n"
    PREMIERED = 'Premiered@([0-9]{4})\\n'
    COUNTRY = 'Country@([a-zA-Z]*)\\n'
    STATUS = 'Status@([a-zA-Z /]*)\\n'
    CLASSIFICATION = 'Classification@([a-zA-Z -]*)\\n'
    GENRES = 'Genres@([a-zA-Z |/\-]*)\\n'
    NETWORK = 'Network@([a-zA-Z |\(\)]*)\\n'
    AIRTIME = 'Airtime@([a-zA-Z0-9 :]*)\\n'
    LEPISODE = 'Latest Episode@([0-9x]*)\^(.*)\^([a-zA-Z0-9/]*)\\n'
    NEPISODE = 'Next Episode@([0-9x]*)\^(.*)\^([a-zA-Z0-9/]*)\\n'

    def __init__(self):
        pass


def regexp_search(pattern, string, number=1, default='N/A'):
    m = reg_search(pattern, string)
    if m is not None:
        return m.group(number)
    else:
        return default