# -*- coding: utf-8 -*-
import scrapy
from Souq.items import SouqItem


class SouqSpider(scrapy.Spider):
    name = 'souq_uae'
    allowed_domains = ['uae.souq.com']
    start_urls = ['https://uae.souq.com/ae-en/shop-all-categories/c/?ref=nav']

    # 解析
    def parse(self, response):
        item = SouqItem()
        title = response.xpath("//h3[@class='shop-all-title']/text()").extract()  # 一级分类名称
        side_navs = response.xpath('//ul[@class="side-nav"]')  # 一級
        hrefs = []
        for side_nav in side_navs:
            titles_strip1 = []
            titles1 = side_nav.xpath('./li/a/text()').extract()
            for x in titles1:
                titles_strip1.append(x.strip())
            lis = side_nav.xpath('./li')
            hrefs1 = []
            for li in lis:
                if li.xpath('./a[@class]'):
                    ul2 = li.xpath('./ul')  # 二级
                    titles_strip2 = []
                    titles2 = ul2.xpath('./li/a/text()').extract()
                    for x in titles2:
                        titles_strip2.append(x.strip())
                    lis2 = ul2.xpath('./li')
                    hrefs2 = []
                    for li2 in lis2:
                        if li2.xpath('./a[@class]'):
                            ul3 = li2.xpath('./ul')  # 三级
                            titles_strip3 = []
                            titles3 = ul3.xpath('./li/a/text()').extract()
                            for x in titles3:
                                titles_strip3.append(x.strip())
                            hrefs3 = ul3.xpath('./li/a/@href').extract()
                            dict3 = self.pack_dict(titles_strip3, hrefs3)
                            hrefs2.append(dict3)
                        else:
                            hrefs2.append(li2.xpath('./a/@href').extract()[0])
                    dict2 = self.pack_dict(titles_strip2, hrefs2)
                    hrefs1.append(dict2)
                else:
                    hrefs1.append(li.xpath('./a/@href').extract()[0])
            dict1 = self.pack_dict(titles_strip1, hrefs1)
            hrefs.append(dict1)
        site = {'site1':self.pack_dict(title, hrefs)}
        item['souq_url_json'] = site
        yield item

    # back
    def pack_dict(self, titles, hrefs):
        packdict = dict(zip(titles, hrefs))
        return packdict
