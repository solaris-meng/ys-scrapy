# -*- coding: utf-8 -*-
import scrapy
import requests
import datetime
import json

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


QT = [
    {'url':'http://m.newsmth.net/board/ChildEducation', 's1':'ChildEducation', 's2':'儿童教育'},
    {'url':'http://m.newsmth.net/board/Universal', 's1':'Universal', 's2':'特快万象'},
    {'url':'http://m.newsmth.net/board/FamilyLife', 's1':'FamilyLife', 's2':'家庭生活'},
    {'url':'http://m.newsmth.net/board/Pregnancy', 's1':'Pregnancy', 's2':'怀孕'},
    {'url':'http://m.newsmth.net/board/PieLove', 's1':'PieLove', 's2':'鹊桥'},
    {'url':'http://m.newsmth.net/board/Picture', 's1':'Picture', 's2':'贴图'},
    {'url':'http://m.newsmth.net/board/RealEstate', 's1':'RealEstate', 's2':'房地产'},
    {'url':'http://m.newsmth.net/board/Occupier', 's1':'Occupier', 's2':'业主之家'},
    {'url':'http://m.newsmth.net/board/OMTV', 's1':'OMTV', 's2':'欧美电视'},
    {'url':'http://m.newsmth.net/board/WorldSoccer', 's1':'WorldSoccer', 's2':'国家足球'},
    {'url':'http://m.newsmth.net/board/WorkLife', 's1':'WorkLife', 's2':'职业生涯'},
    {'url':'http://m.newsmth.net/board/DigiHome', 's1':'DigiHome', 's2':'数字家庭'},
    {'url':'http://m.newsmth.net/board/Divorce', 's1':'Divorce', 's2':'离婚'},
    {'url':'http://m.newsmth.net/board/Movie', 's1':'Movie', 's2':'电影'},
    {'url':'http://m.newsmth.net/board/Children', 's1':'Children', 's2':'孩子'},
    {'url':'http://m.newsmth.net/board/CouponsLife', 's1':'CouponsLife', 's2':'辣妈羊毛党'},
    {'url':'http://m.newsmth.net/board/OurEstate', 's1':'OurEstate', 's2':'二手房交流'},
    {'url':'http://m.newsmth.net/board/ITExpress', 's1':'ITExpress', 's2':'IT特快'},
    {'url':'http://m.newsmth.net/board/SchoolEstate', 's1':'SchoolEstate', 's2':'学区房'},
    {'url':'http://m.newsmth.net/board/EconForum', 's1':'EconForum', 's2':'经济论坛'},
]

INDEX = -1 # for last one
INDEX = -2 # for all

#INDEX = -3 # for cat
#CATE = '健康'

fname = 'shuimu'
DB = 'local'

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

def local_save_json(i):
    l = json.dumps(i,ensure_ascii=False)
    with open('data/%s' % fname, 'a+') as fd:
        fd.write(l+'\n')
def local_save_txt(i, name):
    fname = 'data/%s_%s' % (name, datetime.date.today().strftime('%Y-%m-%d'))

    l = ''
    for k in i:
        l += i[k]
        l += '\t'
    with open(fname, 'a+') as fd:
        fd.write(l+'\n')

class ShuimuSpider(scrapy.Spider):
    name = "shuimu"
    allowed_domains = ["m.newsmth.net"]
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
        for i in range(1, 5):
            url = '%s?p=%d' % (response.url, i)

            req = scrapy.Request(url, callback=self.parse_c0)
            # pass args to sub func
            for i in QT:
                if i['url'] == response.url:
                    req.meta['s1'] = i['s1']
                    req.meta['s2'] = i['s2']
            yield req

    def parse_c0(self, response):
        l = response.xpath('//li')[1:]

        skip = 5
        c = 0
        for i in l:
            c += 1
            if c < skip:
                continue
            #if c > 7:
            #    break

            s_url = i.xpath('div/a/@href').extract()[0]
            f_url = 'http://m.newsmth.net%s' % s_url

            req = scrapy.Request(f_url, callback=self.parse_c1)
            # pass args to sub func
            req.meta['s1'] = response.meta['s1']
            req.meta['s2'] = response.meta['s2']
            yield req

    def parse_c1(self, response):
        p_pages = 1
        for i in response.xpath('//form')[0].xpath('a/text()').extract():
            if len(i.split('/')) == 2:
                p_pages = int(i.split('/')[1])
        p_tl = response.xpath('//li[@class="f"]/text()').extract()[0]

        for i in range(1, p_pages):
            url = '%s?p=%d' % (response.url, i)
            req = scrapy.Request(url, callback=self.parse_c2)
            req.meta['s1'] = response.meta['s1']
            req.meta['s2'] = response.meta['s2']
            req.meta['tl'] = p_tl
            req.meta['url'] = response.url

            yield req

    def parse_c2(self, response):

        lis = response.xpath('//li')
        for com in lis[1:]:
            p_com_name = com.xpath('div/div/a/text()').extract()[1]
            p_com_time = com.xpath('div/div/a/text()').extract()[2]
            p_com_text = com.xpath('div[@class="sp"]/text()').extract()

            i = {}
            i['p_url'] = response.url
            i['p_tl'] = response.meta['tl']
            i['p_s1'] = response.meta['s1']
            i['p_s2'] = response.meta['s2']

            i['p_com_name'] = p_com_name
            i['p_com_time'] = p_com_time
            i['p_com_text'] = ''

            for t in p_com_text:
                i['p_com_text'] += t

            if DB == 'local':
                local_save_json(i)
                local_save_txt(i, i['p_s1'])

            if True:
                print('-----start')
                print(i['p_url'])
                print(i['p_s2'])
                print(i['p_tl'])
                print(p_com_name)
                print(p_com_time)
                print(i['p_com_text'])
                print('-----end')
