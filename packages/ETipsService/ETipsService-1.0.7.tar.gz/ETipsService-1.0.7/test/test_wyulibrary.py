# -*- coding: utf-8 -*-

from service.wyulibrary import WyuLibrary
from service import _

if __name__ == '__main__':
    lib = WyuLibrary()
    print _.to_json_string(lib.search_book("程序设计",1))
    print _.to_json_string(lib.search_book("程序设计",2))
    print(_.to_json_string(lib.search_book(u'Java', 1)))
    print(_.to_json_string(lib.book_status('572952')))
