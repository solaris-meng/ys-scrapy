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
    {'url':'http://www.bilibili.com/video/bangumi-two-1.html', 's1':'番剧', 's2':'连载动画'},
    {'url':'http://www.bilibili.com/video/part-twoelement-1.html', 's1':'番剧', 's2':'完结动画'},
    {'url':'http://www.bilibili.com/video/bangumi_chinese_1.html', 's1':'番剧', 's2':'国产动画'},
]

INDEX = -1 # for last one
INDEX = -2 # for all

#INDEX = -3 # for cat
#CATE = '健康'

fname = 'bilibili'
DB = 'local'

def local_save_json(i):
    l = json.dumps(i,ensure_ascii=False)
    with open('data/%s' % fname, 'a+') as fd:
        fd.write(l+'\n')
def local_save_txt(i):
    l = ''
    l += i['name'] + '\t'
    l += i['url'] + '\t'
    l += i['s1'] + '\t'
    l += i['s2'] + '\t'
    l += i['author'] + '\t'
    l += i['count_view'] + '\t'
    l += i['count_comment'] + '\t'

    with open('data/%s.txt' % fname, 'a+') as fd:
        fd.write(l+'\n')

class BilibiliSpider(scrapy.Spider):
    name = "bilibili"
    allowed_domains = ["www.bilibili.com"]
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
        pages = response.xpath("//span[@class='result custom-right-inner']/text()").extract()[0].split()[1]
        for i in range(1, int(pages)):
            url = '%s#!page=%d' % (response.url, i)

            req = scrapy.Request(url, callback=self.parse_c0)
            # pass args to sub func
            for i in QT:
                if i['url'] == response.url:
                    req.meta['s1'] = i['s1']
                    req.meta['s2'] = i['s2']
            yield req

    def parse_c0(self, response):
        l = response.xpath("//div[@class='l-item']")

        c = 0
        for b in l:
            c += 1

            i = {}
            i['s1'] = response.meta['s1']
            i['s2'] = response.meta['s2']
            i['url'] = b.xpath("a/@href").extract()[0]
            i['name'] = b.xpath("a/@title").extract()[0]
            i['author'] = b.xpath("div/div/a[@class='v-author']/text()").extract()[0]

            its = b.xpath("div/div//span/text()").extract()
            i['count_view'] = its[0]
            i['count_comment'] = its[1]

            print(i['url']+' '+i['name'])

            if DB == 'local':
                local_save_json(i)
                local_save_txt(i)
