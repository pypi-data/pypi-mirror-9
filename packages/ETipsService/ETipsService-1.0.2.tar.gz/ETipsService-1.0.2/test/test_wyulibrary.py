# -*- coding: utf-8 -*-

from service.wyulibrary import WyuLibrary


if __name__ == '__main__':
    lib = WyuLibrary()
    # print urllib.quote('程序设计'.decode('utf').encode('gbk'))
    print lib.search_book("程序设计")
    # print lib.search_book('ruby')