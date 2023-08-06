# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import _

"""
knowning problems:
1.他服务器有防御型，不能频繁请求，不然不行
"""

"""
to do:
1.timeout support
2.管理好错误,异常
3.失败记录下来
"""

apart = {
    '34': '1',
    '35': '9',
    '36': '17',
    '37': '25',
    '1': '33',
    '2': '40',
    '3': '47',
    '4': '55',
    '5': '63',
    '6': '68',
    '19': '74',
    '20': '75',
    '21': '76',
    '22': '77',
    '14': '105',
    '15': '114',
    '38': '122',
    '39': '123',
    '40': '124',
    '41': '214',
    '42': '226',
    '43': '227'
}


class LifeService(object):
    def __init__(self):
        pass

    @staticmethod
    def _get_electricity_info_html( apart_id, meter_room):
        """get html

        :param apart_id: 栋数
        :param meter_room: 宿舍号
        """
        if apart.get(apart_id) is None:
            raise KeyError('not support the apart_id= ' + apart_id)
        post_data = {
            'action': 'search',
            'apartID': apart.get(apart_id),
            'meter_room': apart_id + meter_room
        }
        r = requests.post('http://202.192.252.140/index.asp', data=post_data)
        return r.content.decode(_.get_charset(r.content))


    def get_electricity_info(self, apart_id, meter_room):
        """get electricity info

            :param apart_id: 栋数
            :param meter_room: 宿舍号
        """
        apart_id = str(apart_id)
        meter_room = str(meter_room)
        try:
            content = LifeService._get_electricity_info_html(apart_id, meter_room)
        except KeyError as e:
            _.d(e.message)
            result = {
                'response': None
            }
            return _.to_json_string(result)
        soup = BeautifulSoup(content)
        tags = soup.find_all(name='span', class_='STYLE7')
        result = {
            'response': {
                'apart': _.trim(tags[0].string),
                'apart_id': _.trim(tags[1].string),
                'used': _.trim(tags[2].string),
                'left': _.trim(tags[3].string),
                'update_time': _.trim(tags[4].string)
            }
        }
        return _.to_json_string(result)

