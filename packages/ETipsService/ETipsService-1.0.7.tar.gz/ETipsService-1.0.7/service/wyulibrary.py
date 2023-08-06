# -*- coding: utf-8 -*-

import requests
import _
from bs4 import BeautifulSoup


class WyuLibrary(object):
    url_search = u'http://lib.wyu.edu.cn/opac/searchresult.aspx'
    url_book_info = u'http://lib.wyu.edu.cn/opac/bookinfo.aspx'

    def __init__(self):
        self._timeout = 20  #

    def __search_book_html(self, anywords, page):
        """
        检索图书列表页面
        :param anywords: 关键字
        :param page:  页码
        :return: html code
        """
        _params = {
            'dt': 'ALL',
            'cl': 'ALL',
            'dp': '20',
            'sf': 'M_PUB_YEAR',
            'ob': 'DESC',
            'sm': 'table',
            'dept': 'ALL',
            'ecx': '0',
            'anywords': '',  # not anywords..
            'page': 1
        }

        _headers = {
            'Host': 'lib.wyu.edu.cn',
            'Referer': 'http://lib.wyu.edu.cn/opac/search.aspx',
            'Accept-Language': ':zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4'
        }

        # url要对中文编码..
        _params['anywords'] = anywords.decode('utf-8').encode('gbk')
        _params['page'] = page
        r = requests.get(url=WyuLibrary.url_search, headers=_headers, params=_params, timeout=self._timeout)
        # _.d(r.content.decode(_.get_charset(r.content)))
        return r.content.decode(_.get_charset(r.content))




    def search_book(self, anywords, page=1):
        """
        检索图书
        :param anywords: 检索关键字
        :param page: 页码
        :return: 图书列表
        """
        result = []
        html = self.__search_book_html(anywords, page)
        soup = BeautifulSoup(html)
        tds = soup.select(selector='tbody')[0].select('td')
        cursor = 1
        while cursor < len(tds) / 9:
            s = (cursor - 1) * 9
            num = tds[s].get_text()
            ctrlno = tds[s].input.attrs['value']
            name = tds[s + 1].get_text()
            author = tds[s + 2].get_text()
            press = tds[s + 3].get_text()
            press_time = tds[s + 4].get_text()
            index_num = tds[s + 5].get_text()
            total = tds[s + 6].get_text()
            left = tds[s + 7].get_text()
            addtion = tds[s + 8].get_text().strip('\r\n')  # 相关资源
            book = {
                'num': num,  # 序号
                'ctrlno': ctrlno,  # 图书馆系统控制号(在图书馆的唯一编号)
                'name': name,  # 名称
                'author': author,  # 作者
                'press': press,  # 出版社
                'press_time': press_time,  # 出版时间
                'index_num': index_num,  # 索取号
                'total': total,  # 馆藏
                'left': left,  # 剩余
            }
            result.append(book)
            cursor += 1

        return result

    def __book_status_html(self, ctrlno):
        """
        获取图书借阅页面
        :param ctrlno:
        :return:
        """
        _params = {
            'ctrlno': ctrlno
        }
        _headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Host': 'lib.wyu.edu.cn',
            'Referer': 'http://lib.wyu.edu.cn/opac/searchresult.aspx'
        }
        r = requests.get(url=WyuLibrary.url_book_info, headers=_headers, params=_params, timeout=self._timeout)
        # _.d(r.content.decode(_.get_charset(r.content)))
        return r.content.decode(_.get_charset(r.content))

    def __get_isbn(self, html):
        """
        从图书借阅状态页面中获取isbn
        :param html:
        :return:
        """

        import re

        reg = re.compile(r'getBookCover\(".*","(.*)"\);')
        res = reg.findall(html)
        if len(res) > 0:
            return res[0]
        else:
            return ''

    def book_status(self, ctrlno):
        """
        查看图书借阅情况
        :param ctrlno: 图书馆系统图书唯一标识
        :return: {
            'isbn': '',
            'status_list': [],
        }
        """
        result = {
            'isbn': '',
            'status_list': [],
        }
        html = self.__book_status_html(ctrlno)
        soup = BeautifulSoup(html)

        tds = soup.select(selector='tbody')[0].select('td')
        cursor = 1
        while cursor < len(tds) / 7:
            s = (cursor - 1) * 7
            location = tds[s].get_text().strip('\r\n ')
            index_num = tds[s + 1].get_text().strip('\r\n ')
            login_num = tds[s + 2].get_text().strip('\r\n ')
            volume = tds[s + 3].get_text().strip('\r\n ')
            year = tds[s + 4].get_text().strip('\r\n ')
            status = tds[s + 5].get_text().strip('\r\n ')
            type = tds[s + 6].get_text().strip('\r\n ')

            info = {
                'location': location,  # 馆藏地
                'index_num': index_num,  # 索取号
                'login_num': login_num,  # 登录号
                'volume': volume,  # 卷期
                'year': year,  # 年代
                'status': status,  # 状态
                'type': type,  # 借阅类型
            }
            result['status_list'].append(info)
            cursor += 1
        # isbn
        result['isbn'] = self.__get_isbn(html)
        return result






