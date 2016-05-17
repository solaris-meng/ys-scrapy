# -*- coding: utf-8 -*-
import scrapy
import requests
import json

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


QT = [
    {'url':'http://www.qingting.fm/s/supervcategories/212', 's1':'军事'},
    {'url':'http://www.qingting.fm/s/supervcategories/213', 's1':'历史'},
    {'url':'http://www.qingting.fm/s/supervcategories/214', 's1':'儿童'},
    {'url':'http://www.qingting.fm/s/supervcategories/210', 's1':'娱乐'},
    {'url':'http://www.qingting.fm/s/supervcategories/204', 's1':'女性'},
    {'url':'http://www.qingting.fm/s/supervcategories/201', 's1':'搞笑'},
    {'url':'http://www.qingting.fm/s/supervcategories/116', 's1':'教育'},
    {'url':'http://www.qingting.fm/s/supervcategories/126', 's1':'外语'},
    {'url':'http://www.qingting.fm/s/supervcategories/74', 's1':'公开课'},
    {'url':'http://www.qingting.fm/s/supervcategories/893', 's1':'文化'},
    {'url':'http://www.qingting.fm/s/supervcategories/515', 's1':'评书'},
    {'url':'http://www.qingting.fm/s/supervcategories/217', 's1':'戏曲'},
    {'url':'http://www.qingting.fm/s/supervcategories/215', 's1':'财经'},
    {'url':'http://www.qingting.fm/s/supervcategories/216', 's1':'科技'},
    {'url':'http://www.qingting.fm/s/supervcategories/207', 's1':'汽车'},
    {'url':'http://www.qingting.fm/s/supervcategories/203', 's1':'体育'},
    {'url':'http://www.qingting.fm/s/supervcategories/166', 's1':'校园'},
    {'url':'http://www.qingting.fm/s/supervcategories/205', 's1':'游戏动漫'},
    {'url':'http://www.qingting.fm/s/supervcategories/206', 's1':'广播剧'},
    {'url':'http://www.qingting.fm/s/supervcategories/569', 's1':'电影'},
    {'url':'http://www.qingting.fm/s/supervcategories/674', 's1':'旅游'},
    {'url':'http://www.qingting.fm/s/supervcategories/732', 's1':'自媒体'},
    {'url':'http://www.qingting.fm/s/supervcategories/818', 's1':'时尚'},
]
INDEX = -1 # for last one

INDEX = -2 # for all

#INDEX = -3 # for cat
#CATE = '健康'

f_cat = 'qingting_category.txt'
DB = 'local'
DB = 'all'

def send_item_v1(item):
    url1='http://101.200.174.136:10086/api/qingtingfm/channels'
    #url2='http://101.200.174.136:10222/api/qingtingfm/channels'
    data = {
        'id': item['id'],
        'name': item['name'],
        'desc': item['des'],
        'img_url': item['img_url'],
        'clist': item['clist'],
        'ourl': item['ourl'],
        's1': item['s1'],
        's2': item['s2'],
        's3': item['s3']
    }
    rv = requests.post(url1, data)

    print 'name-%s, %d' % (item['name'], rv.status_code)
    return 'success'

class Qingting2Spider(scrapy.Spider):
    name = "qingting2"
    allowed_domains = ["qingting.fm"]
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
        cates = response.xpath('//div[@class="right-bar clearfix"]')
        for c in cates:
            s2 = c.xpath('div[@class="title pull-left"]/text()').extract()[0]
            url = 'http://www.qingting.fm/s%s' % c.xpath('a/@href').extract()[0]
            print(s2,url)
            req = scrapy.Request(url, callback=self.parse_cate)

            for i in QT:
                if i['url'] == response.url:
                    s1 = i['s1']
            req.meta['s1'] = s1
            req.meta['s2'] = s2
            req.meta['fname'] = s1

            with open(f_cat, 'a+') as fd:
                line = '%s\t%s\n' % (req.meta['s1'], req.meta['s2'])
                fd.write(line)
            yield req

    def parse_cate(self, response):
        items = response.xpath("//a/@href").extract()
        s1 = response.meta['s1']
        s2 = response.meta['s2']
        fname = response.meta['fname']
        for i in items:
            url = 'http://www.qingting.fm/s%s' % i
            #print url
            req = scrapy.Request(url, callback=self.parse_item)
            req.meta['s1'] = s1
            req.meta['s2'] = s2
            req.meta['fname'] = fname
            yield req
        pass

    def parse_item(self, response):
        p_url = response.url

        p_cate_1 = response.meta['s1']
        p_cate_2 = response.meta['s2']
        p_cate_3 = 'init'
        fname = response.meta['fname']

        p_name = response.xpath('//div[@class="channel-name"]/text()').extract()[0]

        if p_cate_1 == '电台':
            p_des = response.xpath('//div[@class="abstract"]/div[@class="content"]/text()').extract()[0]
        else:
            p_des = response.xpath('//div[@class="abstract clearfix"]/div[@class="content"]/text()').extract()[0]

        p_list = response.xpath('//div[@class="left-text"]/span/text()').extract()
        p_img = response.xpath('//img/@src').extract()[0]

        item = {}
        item['id'] = p_url.split('/')[-1]
        item['name'] = p_name
        item['des'] = p_des
        item['img_url'] = p_img
        item['ourl'] = p_url
        item['s1'] = p_cate_1
        item['s2'] = p_cate_2
        item['s3'] = p_cate_3


        item['clist'] = ''
        for i in p_list:
            item['clist'] += '%s###' % i
        item['clist'] = item['clist'][:-3]

        if DB == 'local' or DB == 'all':
            item_json = json.dumps(item,ensure_ascii=False)
            with open(fname, 'a+') as fd:
                fd.write(item_json)
                fd.write('\n')
        if DB == 'test_mongo' or DB == 'all':
            send_item_v1(item)
