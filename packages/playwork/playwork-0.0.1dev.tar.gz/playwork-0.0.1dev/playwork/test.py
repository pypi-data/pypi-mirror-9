# -*- coding: utf-8 -*-
# author  : younger shen
# email   : younger.x.shen@gmail.com
# project : Playwork
# date    : 15/1/10 下午6:04
from playwork.routes import Route
from playwork.utils import url_parser

def testRoute():

    Route.controller('/index/name', 'test', 'test')
    url_parser()

def main():
    testRoute()

if __name__ == '__main__':
    main()