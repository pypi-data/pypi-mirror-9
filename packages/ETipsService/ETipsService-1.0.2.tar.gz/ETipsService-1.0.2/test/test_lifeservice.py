# -*- coding: utf-8 -*-

from service.lifeService import LifeService


if __name__ == '__main__':
    service = LifeService()
    print service.get_electricity_info(3, 706)



