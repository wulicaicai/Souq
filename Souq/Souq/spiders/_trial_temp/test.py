import pymongo

import requests
from lxml import etree


class QiushiSpider:
    def __init__(self):
        self.url = 'https://saudi.souq.com/sa-en/casio-a-glance-men-s-grey-dial-resin-band-watch-w-735h-8av-5822010/i/'
        self.headers = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'}

    # 获取页面
    def getPage(self):
        html = requests.get(self.url, headers=self.headers).text
        # print(html)
        self.parsePage(html)

    # 解析
    def parsePage(self, html):
        # 两步走
        parseHtml = etree.HTML(html)
        discount_price = parseHtml.xpath(
            "//h3[@class='price is sk-clr1']//text()")
        money = discount_price[2]
        print(money) #SAR
        discount_price = discount_price[1].replace('\n', '').strip()
        discount_price = discount_price+money
        discount_price=discount_price.strip()
        print(discount_price)



    # 主函数
    def workOn(self):
        print('正在爬取中......')
        self.getPage()
        print('爬取结束')


if __name__ == '__main__':
    spider = QiushiSpider()
    spider.workOn()