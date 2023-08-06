#!/usr/bin/env python
#coding:utf-8
'''
Created on 2015年3月14日
@author: zhaohf
'''
import pweather
import sys
def main():
    if len(sys.argv) < 2:
        print '请输入要查询的城市拼音！'
        print 'Usage:pweather shanghai<or other city name in Chinese pinyin>'
        sys.exit(0)
    cityname = sys.argv[1]
    pweather.get_response(cityname)
