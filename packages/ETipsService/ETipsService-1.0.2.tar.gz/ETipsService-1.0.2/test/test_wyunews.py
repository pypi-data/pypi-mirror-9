# -*- coding: utf-8 -*-

from service.wyunews import WyuNews

if __name__ == '__main__':
    wyunews = WyuNews()
    print (wyunews.get_wyu_news(1))

    print wyunews.get_news_content('http://www.wyu.cn/news/news_zxtz/201481811490835123.htm')