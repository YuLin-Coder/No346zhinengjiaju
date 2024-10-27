# 数据容器文件

import scrapy

class SpiderItem(scrapy.Item):
    pass

class BingxiangxinxiItem(scrapy.Item):
    # 来源
    laiyuan = scrapy.Field()
    # 封面
    fengmian = scrapy.Field()
    # 标题
    biaoti = scrapy.Field()
    # 价格
    jiage = scrapy.Field()
    # 品牌
    pinpai = scrapy.Field()
    # 商品名称
    spmc = scrapy.Field()
    # 商品产地
    spcd = scrapy.Field()
    # 能效等级
    nxdj = scrapy.Field()
    # 门款式
    mks = scrapy.Field()
    # 制冷方式
    zlfs = scrapy.Field()
    # 主色系
    zhusexi = scrapy.Field()

