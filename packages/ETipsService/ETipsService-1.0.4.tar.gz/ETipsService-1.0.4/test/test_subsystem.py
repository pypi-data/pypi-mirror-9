# -*- coding: utf-8 -*-

from service.subsystem import SubSystem


if __name__ == '__main__':
    u = SubSystem("3112002722", '931127')
    # print u.login()
    if u.login():
        print "****************Login success!**************"
        print "****************course list**************"
        print u.get_course()
        print u.get_score()
        u._get_stu_info()