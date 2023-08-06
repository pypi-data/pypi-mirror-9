__author__ = 'Gabriel Melillo<gabriel@melillo.me>'
__version__ = '0.1'

from datetime import datetime, timedelta


def str2time(time):
    return datetime.strptime(time, '%b/%d/%Y')


def time2str(time=datetime.now()):
    return time.strftime("%b/%d/%Y")


def get_offset_time(str_time, offset=0):
    try:
        return time2str(str2time(str_time) + timedelta(days=offset))
    except ValueError:
        return "N/A"