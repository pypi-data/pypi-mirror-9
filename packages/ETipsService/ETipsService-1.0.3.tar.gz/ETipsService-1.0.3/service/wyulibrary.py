# -*- coding: utf-8 -*-

import requests
import _
from bs4 import BeautifulSoup


class WyuLibrary(object):
    url_search = u'http://lib.wyu.edu.cn/opac/searchresult.aspx'

    def __init__(self):
        self._headers = {
            'Host': 'lib.wyu.edu.cn',
            'Referer': 'http://lib.wyu.edu.cn/opac/search.aspx',
            'Accept-Language': ':zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
        }

        self._params = {
            'dt': 'ALL',
            'cl': 'ALL',
            'dp': '20',
            'sf': 'M_PUB_YEAR',
            'ob': 'DESC',
            'sm': 'table',
            'dept': 'ALL',
            'ecx': '0',
            'anywords': ''  # not anywords..
        }

        self._timeout = 20  #

    def _search_book_html(self, anywords):
        # url要对中文编码..
        self._params['anywords'] = anywords.decode('utf-8').encode('gbk')
        r = requests.get(url=WyuLibrary.url_search, headers=self._headers, params=self._params, timeout=self._timeout)
        # _.d(r.content.decode(_.get_charset(r.content)))
        return r.content.decode(_.get_charset(r.content))

    def search_book(self, anywords):
        result = {
            'response': []
        }
        html = self._search_book_html(anywords)
        soup = BeautifulSoup(html)
        tds = soup.select(selector='tbody')[0].select('td')
        cursor = 1
        while cursor < len(tds) / 9:
            s = (cursor - 1) * 9
            num = tds[s].get_text()
            name = tds[s + 1].get_text()
            author = tds[s + 2].get_text()
            press = tds[s + 3].get_text()
            press_time = tds[s + 4].get_text()
            index_num = tds[s + 5].get_text()
            total = tds[s + 6].get_text()
            left = tds[s + 7].get_text()
            addtion = tds[s + 8].get_text()
            book = {
                'name': name,
                'author': author,
                'press': press,
                'press_time': press_time,
                'index_num': index_num,
                'total': total,
                'left': left,
                'addtion': addtion
            }
            result['response'].append(book)
            cursor += 1
        return result





