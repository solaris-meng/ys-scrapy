# -*- coding: utf-8 -*-
import scrapy
import requests
import datetime
import json
import jieba
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


QT = [
    {'url':'http://www.juji123.com/dongman'},
]

INDEX = -1 # for last one
INDEX = -2 # for all

#INDEX = -3 # for cat
#CATE = '健康'

fname = 'juji123'
DB = 'local'

def local_save_json(i):
    l = json.dumps(i,ensure_ascii=False)
    with open('data/%s' % fname, 'a+') as fd:
        fd.write(l+'\n')
def local_save_txt(i):
    l = ''
    l += i['url'] + '\t'
    l += i['name'] + '\t'
    l += i['time'] + '\t'
    for t in i['tags']:
        l += t + '\t'

    with open('data/%s.txt' % fname, 'a+') as fd:
        fd.write(l+'\n')

class Juji123Spider(scrapy.Spider):
    name = "juji123"
    allowed_domains = ["www.juji123.com", "juji123.com"]
    start_urls = []

    if INDEX == -1:
        start_urls.append(QT[-1]['url'])
    elif INDEX == -2:
        for i in QT:
            start_urls.append(i['url'])
    elif INDEX == -3:
        for i in QT:
            if i['s1'] != CATE:
                continue
            start_urls.append(i['url'])
    else:
        start_urls.append(QT[INDEX]['url'])

    def parse(self, response):
        # get pages
        pages = 83
        for i in range(1, int(pages)):
            url = '%slist_u_%d.html' % (response.url, i)
            print(url)
            req = scrapy.Request(url, callback=self.parse_c0)
            yield req

    def parse_c0(self, response):
        print(response.url)
        l = response.xpath("//ul[@class='clearfix']/li")

        c = 0
        for b in l:
            c += 1

            i = {}
            i['url'] = b.xpath("div[@class='tit']/h5/a/@href").extract()[0]
            i['name'] = b.xpath("div[@class='tit']/h5/a/text()").extract()[0]
            i['time'] = b.xpath("p[@class='cyear']/text()").extract()[0].split('：')[1].split()[0]
            i['tags'] = b.xpath("p[@class='ctags']/span/text()").extract()

            print(i['url'])
            print(i['name'])
            print(i['time'])
            print(i['tags'])

            if DB == 'local':
                local_save_json(i)
                local_save_txt(i)
