# -*- coding: utf-8 -*-

from service.wyunews import WyuNews
import json
if __name__ == '__main__':
    wyunews = WyuNews()
    print (json.dumps(wyunews.get_wyu_news(1)))

    # print wyunews.get_news_content('http://www.wyu.cn/news/news_zxtz/201481811490835123.htm')
    # print wyunews.get_news_content('http://www.wyu.cn/news/news_xnxw/20153181021141118.htm')
    print wyunews.get_news_content('http://www.wyu.cn/news/news_xnxw/201531811505485186.htm')