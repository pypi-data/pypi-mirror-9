from setup import __version__ as version

__author__ = "Gabriel Melillo<gabriel@melillo.me>"
__version__ = version

import mechanize
from uuid import uuid3, NAMESPACE_OID
from urllib import urlencode
from regexp import regexp_search, Expression
from httplib2 import Http
from bs4 import BeautifulSoup
from datetime import datetime
from socket import error as socket_error


class List(object):
    list = []

    def __init__(self, default=[]):
        self.list = default

    def __getitem__(self, item):
        return self.list[item]

    def __iter__(self):
        for item in self.list:
            yield item

    def __len__(self):
        return len(self.list)

    def __setitem__(self, key, value):
        self.list[key] = value

    def __repr__(self):
        return repr(self.list)

    def __str__(self):
        return self.__repr__()

    def _add_value(self, value):
        for item in self.list:
            if item == value:
                return False
        self.list.append(value)
        return True


class NextEpisode(List):
    def __init__(self, username, password, autologin=True, autoupdate=True):
        super(List, self).__init__()
        self.browser = mechanize.Browser()
        self.add_show = self._add_value
        self.today_list = []

        self._cache_dir = '/tmp/.necd'
        self._logghedin = False
        self._username = username
        self._password = password

        if autologin:
            self.do_login(
                username=username,
                password=password
            )

        if autoupdate:
            self.update_list()

    def do_login(self, username, password):
        self.browser.open("http://next-episode.net/")
        self.browser.select_form(name="login")
        self.browser.form['username'] = username
        self.browser.form['password'] = password
        self.browser.submit()
        self._logghedin = True

    def update_list(self):
        if not self._logghedin:
            self.do_login(self._username, self._password)

        html = self.browser.open('http://next-episode.net/settings?action=manageWL').read()
        soup = BeautifulSoup(html)
        divs = soup.findAll('div',
                            attrs={
                                'class': 'leftColumn'
                            })
        self.list = []
        for div in divs:
            links = div.findAll('a', attrs={'class': 'name'})
            for link in links:
                if link.contents[0] == "V":
                    link.contents[0] = "V (2009)"
                try:
                    self._add_value({
                        'Name': [link.contents[0]],
                        'index': uuid3(NAMESPACE_OID, link.get('href').encode('utf8', 'ignore')).__str__(),
                        'URL': link.get('href').encode('utf8', 'ignore')
                    })
                except UnicodeDecodeError:
                    self._add_value({
                        'Name': [link.contents[0]],
                        'index': 'N/A',
                        'URL': link.get('href').encode('utf8', 'ignore')
                    })

    def attach_tvrage_info(self):
        for idx, show in enumerate(self.list):
            h = Http(self._cache_dir)
            url = "http://services.tvrage.com/tools/quickinfo.php?{}".format(
                urlencode({
                    'show': show['Name'][0].__str__(),
                    'exact': 1
                })
            )

            try:
                resp, content = h.request(url)
            except socket_error:
                resp, content = ("", "")

            _today = datetime.now().strftime("%b/%d/%Y")

            self.list[idx]['TV Rage'] = {
                'Show ID': regexp_search(Expression.SHOW_ID, content),
                'Show Name': regexp_search(Expression.SHOW_NAME, content),
                'URL': regexp_search(Expression.URL, content),
                'Premiered': regexp_search(Expression.PREMIERED, content),
                'Country': regexp_search(Expression.COUNTRY, content),
                'Status': regexp_search(Expression.STATUS, content),
                'Classification': regexp_search(Expression.CLASSIFICATION, content),
                'Genres': regexp_search(Expression.GENRES, content),
                'Network': regexp_search(Expression.NETWORK, content),
                'Airtime': regexp_search(Expression.AIRTIME, content),
                'Latest Episode': {
                    'Number': regexp_search(Expression.LEPISODE, content, number=1),
                    'Title': regexp_search(Expression.LEPISODE, content, number=2),
                    'Air Date': regexp_search(Expression.LEPISODE, content, number=3)
                },
                'Next Episode': {
                    'Number': regexp_search(Expression.NEPISODE, content, number=1),
                    'Title': regexp_search(Expression.NEPISODE, content, number=2),
                    'Air Date': regexp_search(Expression.NEPISODE, content, number=3)
                }
            }

            if _today == self.list[idx]['TV Rage']['Next Episode']['Air Date']:
                self.today_list.append(self.list[idx])
            if _today == self.list[idx]['TV Rage']['Latest Episode']['Air Date']:
                self.today_list.append(self.list[idx])