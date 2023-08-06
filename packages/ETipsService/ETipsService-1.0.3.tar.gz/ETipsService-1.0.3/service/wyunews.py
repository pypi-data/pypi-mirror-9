# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import _


class WyuNews(object):
    def __init__(self):
        pass

    @staticmethod
    def __get_tag_a(tag):
        if tag.has_attr('href') and tag.has_attr('target'):
            if 'http://' in tag.attrs['href']:
                return False
            return True
        return False

    @staticmethod
    def __get_tag_td(tag):
        if tag.has_attr('height') and tag['height'] == '18' and tag.get_text() != '':
            return True
        return False

    @staticmethod
    def __wyu_news(page):
        url = 'http://www.wyu.cn/news/default.asp'
        params = {'page': page}
        r = requests.get(url, params=params)
        encoding = _.get_charset(r.content)
        return r.content.decode(encoding)

    @staticmethod
    def __get_tag_table(tag):
        if tag.has_attr('width') and tag['width'] == '87%' and tag.has_attr('border') and tag.has_attr(
                'align') and tag.has_attr('cellpadding'):
            return True
        return False


    @staticmethod
    def __wyu_news_content(url):
        r = requests.get(url)
        encoding = _.get_charset(r.content)
        return r.content.decode(encoding)

    @staticmethod
    def __get_news_type(tag):
        return tag.get_text().split(u"  ")[0].lstrip(u'【').rstrip(u'】')

    @staticmethod
    def __get_news_from(tag):
        return tag.get_text().split(u"  ")[1].lstrip(u' ').rstrip(u' ')

    @staticmethod
    def __get_news_posttime(tag):
        return tag.get_text().split(u"  ")[2].strip(u' ')

    def get_wyu_news(self, page):
        """获取新闻列表

        :param page: 页码
        :return: json
        """
        response = {
            'result': []
        }
        if page <= 0:
            return response
        res = WyuNews.__wyu_news(page)
        soup = BeautifulSoup(res, from_encoding='utf-8')
        tag_a = soup.find_all(self.__get_tag_a)
        tag_td = soup.find_all(self.__get_tag_td)
        result = []

        for index, item in enumerate(tag_a):
            result.append({
                'url': ''.join(('http://www.wyu.cn/news/', item.attrs['href']))
                , 'title': item.string
                , 'type': self.__get_news_type(tag_td[index])
                , 'from': self.__get_news_from(tag_td[index])
                , 'posttime': self.__get_news_posttime(tag_td[index])
            })
        response['result'] = result
        return _.to_json_string(response)

    def get_news_content(self, url):
        """获取新闻内容

        :param url: 新闻url
        :return: html code
        """
        res = WyuNews.__wyu_news_content(url)
        soup = BeautifulSoup(res, from_encoding='utf-8')
        tag_table = soup.find(self.__get_tag_table)

        tr = tag_table.findAll('tr')[4]
        html = u'<html><head><meta charset="utf-8"></head><body><table  align="center" border="0" cellpadding="0" cellspacing="2" width="75%"><tbody>' + \
               tr.decode() + u'</tbody></table></body></html>'
        return html

