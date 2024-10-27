# 数据爬取文件

import scrapy
import pymysql
import pymssql
from ..items import BingxiangxinxiItem
import time
import re
import random
import platform
import json
import os
from urllib.parse import urlparse
import requests

# 冰箱信息
class BingxiangxinxiSpider(scrapy.Spider):
    name = 'bingxiangxinxiSpider'
    spiderUrl = 'https://search-x.jd.com/Search?area=19&enc=utf-8&keyword=%E5%86%B0%E7%AE%B1%E6%B4%97%E8%A1%A3%E6%9C%BA&adType=7&urlcid3=878&page={}&ad_ids=291%3A33&xtest=new_search&_=1674997398691'
    start_urls = spiderUrl.split(";")
    protocol = ''
    hostname = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start_requests(self):

        plat = platform.system().lower()
        if plat == 'linux' or plat == 'windows':
            connect = self.db_connect()
            cursor = connect.cursor()
            if self.table_exists(cursor, '48dht_bingxiangxinxi') == 1:
                cursor.close()
                connect.close()
                self.temp_data()
                return

        pageNum = 1 + 1
        for url in self.start_urls:
            for page in range(1, pageNum):
                next_link = url.format(page)
                yield scrapy.Request(
                    url=next_link,
                    callback=self.parse
                )

    # 列表解析
    def parse(self, response):
        
        _url = urlparse(self.spiderUrl)
        self.protocol = _url.scheme
        self.hostname = _url.netloc
        plat = platform.system().lower()
        if plat == 'windows_bak':
            pass
        elif plat == 'linux' or plat == 'windows':
            connect = self.db_connect()
            cursor = connect.cursor()
            if self.table_exists(cursor, '48dht_bingxiangxinxi') == 1:
                cursor.close()
                connect.close()
                self.temp_data()
                return

        data = json.loads(response.body)
        list = data["291"]
        
        for item in list:

            fields = BingxiangxinxiItem()


            fields["laiyuan"] = item["link_url"]
            fields["fengmian"] = 'https://img12.360buyimg.com/n7/' + item["image_url"]
            fields["biaoti"] = self.remove_html(item["ad_title"])
            fields["jiage"] = item["pc_price"]

            detailUrlRule = item["link_url"]

            yield scrapy.Request(url=detailUrlRule, meta={'fields': fields}, callback=self.detail_parse)

    # 详情解析
    def detail_parse(self, response):
        fields = response.meta['fields']

        fields["pinpai"] = self.remove_html(response.css('a[clstag="shangpin|keycount|product|pinpai_1"]::text').extract_first())
        fields["spmc"] = re.findall(r'''<ul class="parameter2 p-parameter-list">
                                <li title='(.*?)'>商品名称：''', response.text, re.S)[0].strip()
        fields["spcd"] = re.findall(r'''<ul class="parameter2 p-parameter-list">.*<li title='(.*?)'>商品产地：''', response.text, re.DOTALL)[0].strip()
        fields["nxdj"] = re.findall(r'''<ul class="parameter2 p-parameter-list">.*<li title='(.*?)'>能效等级：''', response.text, re.DOTALL)[0].strip()
        fields["mks"] = re.findall(r'''<ul class="parameter2 p-parameter-list">.*<li title='(.*?)'>门款式：''', response.text, re.DOTALL)[0].strip()
        fields["zlfs"] = re.findall(r'''<ul class="parameter2 p-parameter-list">.*<li title='(.*?)'>制冷方式：''', response.text, re.DOTALL)[0].strip()
        fields["zhusexi"] = re.findall(r'''<ul class="parameter2 p-parameter-list">.*<li title='(.*?)'>主色系：''', response.text, re.DOTALL)[0].strip()
        
        return fields


    # 去除多余html标签
    def remove_html(self, html):
        if html == None:
            return ''
        pattern = re.compile(r'<[^>]+>', re.S)
        return pattern.sub('', html).strip()

    # 数据库连接
    def db_connect(self):
        type = self.settings.get('TYPE', 'mysql')
        host = self.settings.get('HOST', 'localhost')
        port = int(self.settings.get('PORT', 3306))
        user = self.settings.get('USER', 'root')
        password = self.settings.get('PASSWORD', '123456')

        try:
            database = self.databaseName
        except:
            database = self.settings.get('DATABASE', '')

        if type == 'mysql':
            connect = pymysql.connect(host=host, port=port, db=database, user=user, passwd=password, charset='utf8')
        else:
            connect = pymssql.connect(host=host, user=user, password=password, database=database)

        return connect

    # 断表是否存在
    def table_exists(self, cursor, table_name):
        cursor.execute("show tables;")
        tables = [cursor.fetchall()]
        table_list = re.findall('(\'.*?\')',str(tables))
        table_list = [re.sub("'",'',each) for each in table_list]

        if table_name in table_list:
            return 1
        else:
            return 0

    # 数据缓存源
    def temp_data(self):

        connect = self.db_connect()
        cursor = connect.cursor()
        sql = '''
            insert into bingxiangxinxi(
                laiyuan
                ,fengmian
                ,biaoti
                ,jiage
                ,pinpai
                ,spmc
                ,spcd
                ,nxdj
                ,mks
                ,zlfs
                ,zhusexi
            )
            select
                laiyuan
                ,fengmian
                ,biaoti
                ,jiage
                ,pinpai
                ,spmc
                ,spcd
                ,nxdj
                ,mks
                ,zlfs
                ,zhusexi
            from 48dht_bingxiangxinxi
            where(not exists (select
                laiyuan
                ,fengmian
                ,biaoti
                ,jiage
                ,pinpai
                ,spmc
                ,spcd
                ,nxdj
                ,mks
                ,zlfs
                ,zhusexi
            from bingxiangxinxi where
             bingxiangxinxi.laiyuan=48dht_bingxiangxinxi.laiyuan
            and bingxiangxinxi.fengmian=48dht_bingxiangxinxi.fengmian
            and bingxiangxinxi.biaoti=48dht_bingxiangxinxi.biaoti
            and bingxiangxinxi.jiage=48dht_bingxiangxinxi.jiage
            and bingxiangxinxi.pinpai=48dht_bingxiangxinxi.pinpai
            and bingxiangxinxi.spmc=48dht_bingxiangxinxi.spmc
            and bingxiangxinxi.spcd=48dht_bingxiangxinxi.spcd
            and bingxiangxinxi.nxdj=48dht_bingxiangxinxi.nxdj
            and bingxiangxinxi.mks=48dht_bingxiangxinxi.mks
            and bingxiangxinxi.zlfs=48dht_bingxiangxinxi.zlfs
            and bingxiangxinxi.zhusexi=48dht_bingxiangxinxi.zhusexi
            ))
            limit {0}
        '''.format(random.randint(20,30))

        cursor.execute(sql)
        connect.commit()

        connect.close()
