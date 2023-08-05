# -*- coding: utf-8 -*-
# author  : younger shen
# email   : younger.x.shen@gmail.com
# project : Playwork
# date    : 15/1/10 下午10:03

class Route(object):

    def __init__(self):
        pass

    @classmethod
    def controller(cls, url, controller, name=None, namespace=None):
        print cls
        print url
        print controller
        print name
        print namespace