#!/usr/bin/env python
#coding:utf-8
'''
Created on 2015年3月14日
@author: zhaohf
'''
import sys,json,urllib2
from termcolor import colored

def get_response(cityname):
    url = 'http://apistore.baidu.com/microservice/weather?citypinyin=%s' % cityname
    jsons = json.load(urllib2.urlopen(url))
    errNum = jsons['errNum']
    if errNum == -1:
        print '请输入正确的城市拼音！'
        sys.exit(0)
    retData = jsons['retData']
    print u'今日 ' + colored(retData['city'],'blue') + u' 的天气情况如下:'
    print u'天气:' + colored(retData['weather'],'green') + u'\t温度:' + colored(retData['temp'],'green')
    print u'最低温迪:'+ colored(retData['l_tmp'],'green') + '\t'+u'最高温度:'+colored(retData['h_tmp'],'green')
    print u'风向:' + colored(retData['WD'],'green') + '\t' + u'风力:'+colored(retData['WS'],'green')
    print u'日出时间:' + colored(retData['sunrise'],'green') + '\t' + u'日落时间:' +colored(retData['sunset'],'green')
