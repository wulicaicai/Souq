# -*- coding: utf-8 -*-
from urllib.parse import urlparse
import re, time, json, requests, scrapy, os
from Souq.items import SouqItem


def get(session, url, retry=5, *args, **kwargs):
    re_time = 0
    res = None
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15

    while re_time < retry:
        re_time += 1
        try:
            res = session.get(url, *args, **kwargs)
            res.raise_for_status()
            break
        except:
            print("网络错误,正在重试 [%s] 次." % re_time)
            time.sleep(1.5)
    return res


def post(session, url, post_data, retry=5, *args, **kwargs):
    re_time = 0
    res = None
    if "timeout" not in kwargs:
        kwargs["timeout"] = 15
    while re_time < retry:
        re_time += 1
        try:
            res = session.post(url, post_data, *args, **kwargs)
            break
        except:
            print("网络错误,正在重试 [%s] 次." % re_time)
            # change_local_ip_pool()
            time.sleep(1.5)
    return res


class SouqSpider(scrapy.Spider):
    name = 'souq_product'
    url = 'http://third.gets.com/api/index.php?act=getSouqCategory&sec=20171212getscn&site=2'
    # url2 = 'https://saudi.souq.com'
    start_spider_url = []
    start_spider_path = []
    req = get(requests.session(), url)
    res = json.loads(req.text.encode('utf-8').decode('utf-8-sig'))  # req 带有bom头 需要先转字节流,后再转为没有bom的urf-8-sig即可
    allowed_domains = ['saudi.souq.com']

    for r in res:
        classid = r
        start_spider_url.append(res[str(r)]['url'] + '_' + classid)
    for spider_url in start_spider_url:
        # pat_h = urlparse(p)
        # start_spider_path.append(pat_h.path)
        spider_url_re = re.compile(r'(https\:\/\/.*?)_.*')
        start_url_spider_url = spider_url_re.findall(spider_url)
        start_urls = [start_url_spider_url[0]]

    # 解析
    def parse(self, response):
        # l = os.path.dirname(os.path.realpath(__file__))
        with open('souq_prjduct.txt', 'a', encoding='utf-8') as f:
            x = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            f.write(x + '\n')
        for spider_url in self.start_spider_url:
            spider_url_re = re.compile(r'(https\:\/\/.*?)_.*')
            start_url_spider_url = spider_url_re.findall(spider_url)
            spider_url_id = re.compile(r'https\:\/\/.*?_(.*)')
            spider_id = spider_url_id.findall(spider_url)
            for num in range(6):
                url = start_url_spider_url[0] + '?section=2&page=' + str(num)
                yield scrapy.Request(url, callback=self.parseHtml, meta={'spider_id': spider_id})

    def parseHtml(self, response):
        baseList = response.xpath(
            "//div[@class='grid-list search-results-content']//div[@class='column column-block block-grid-large single-item']/div[@class='row']/div[@class='columns small-12']/div[@class='img-bucket']/a/@href").extract()
        # print(baseList)
        for l in baseList:
            link = l
            spider_id = response.meta['spider_id']
            yield scrapy.Request(l, callback=self.parseInfo, meta={'item': link, 'spider_id': spider_id})

    def parseInfo(self, response):
        item = SouqItem()

        link = response.meta['item']
        spider_id = response.meta['spider_id']

        product_id = response.xpath(
            "//span[@class='star-rating product-stars']//input[@id='id_item']/@value").extract()  # 产品id
        product_id = product_id[0]
        product_url = link  # 差评链接
        # time.sleep(2.5)
        images = '|'.join(response.xpath(
            "//div[@class='slick-list draggable']//div[@class='slick-track']//div[@class='slide slick-slide']//a//div[@class='img-bucket zoom-enabled']/img/@src | //div[@class='img-bucket ']//img/@src | //a[@data-open='product-gallery-modal']/div[@class='img-bucket zoom-enabled']/img/@data-url").extract())  # 产品大图
        title = response.xpath(
            "//div[@class='small-12 columns product-title']/h1//font/text() | //div[@class='small-12 columns product-title']/h1/text()").extract()  # 标题
        title = title[0]
        if response.xpath("//meta[@name='keywords']/@content").extract():  # 商品关键字
            keywords = response.xpath("//meta[@name='keywords']/@content").extract()
        else:
            keywords = ''

        if response.xpath("//div[@id='description-short']/p/text()").extract():  # 商品描述
            description = response.xpath("//div[@id='description-short']/p/text()").extract()
            description = description[0].strip()
        else:
            if response.xpath("//div[@id='description-full']/p/text()").extract():
                description = response.xpath("//div[@id='description-short']/p/text()").extract()
                description = description[0].strip()
            else:
                description = response.xpath("//meta[@name='description']/@content").extract()
                description = description[0].strip()

        discount_price = response.xpath("//h3[@class='price is sk-clr1']//text()").extract()  # 折扣价
        money = discount_price[2]
        discount_price = discount_price[1].replace('\n', '').strip()
        discount_price = discount_price + money
        discount_price = discount_price.strip()

        if response.xpath("//span[@class='was']//text()").extract():  # 价格
            price = response.xpath("//span[@class='was']//text()").extract()
            price = price[0].replace('\n', '').strip()
        else:
            price = discount_price

        if response.xpath(
                "//div[@class='reviews-total']/span/font[@class]//text() | //div[@class='rate-of-avg']//strong/text()").extract():  # 反馈数
            feedback = response.xpath(
                "//div[@class='reviews-total']/span/font[@class]//text() | //div[@class='rate-of-avg']//strong/text()").extract()
            feedback = feedback[0].strip()
        else:
            feedback = ''
        if response.xpath('//span[@data-toggle="Fullfilled-tooltip"]/img/@src'):  # 是否为fba产品
            fba = '1'
            print(
                'fba=1---------------------------------------------------------------------------------------------------')
        else:
            fba = '0'

        if response.xpath(
                "//div[@class='star-rating mainRating']/div[@class]/div[@class='avg space']/strong/text() | //div[@class='hide-for-small-only']/div/strong/font/font/text() | //div[@class='mainRating clearfix ']/div[@class='hide-for-small-only']/div[@class='avg']/strong/text() |//div[@class='mainRating clearfix']/div[@class='hide-for-small-only']/div[@class='avg']/strong/text()").extract():  # 星级
            starts = response.xpath(
                "//div[@class='star-rating mainRating']/div[@class]/div[@class='avg space']/strong/text() | //div[@class='hide-for-small-only']/div/strong/font/font/text() | //div[@class='mainRating clearfix ']/div[@class='hide-for-small-only']/div[@class='avg']/strong/text() |//div[@class='mainRating clearfix']/div[@class='hide-for-small-only']/div[@class='avg']/strong/text()").extract()
            starts = starts[0].strip()
            print(starts)
        else:
            starts = ''

        if response.xpath(
                "//span[@class='star-rating product-stars']//a[@class='linkToReviewsTab']//text()").extract():  # 评论数
            revier = response.xpath(
                "//span[@class='star-rating product-stars']//a[@class='linkToReviewsTab']//text()").extract()
            re_1 = re.compile(r"(\d+).*")
            revier = re_1.findall(revier[0])[0]
        else:
            revier = ''

        if response.xpath(
                "//div[@class='small-12 columns product-title']/span/a[1]/font//text() | //div[@class='small-12 columns product-title']/span/a[1]/text()").extract():  # 品牌名
            brand = response.xpath(
                "//div[@class='small-12 columns product-title']/span/a[1]/font//text() | //div[@class='small-12 columns product-title']/span/a[1]/text()").extract()
            brand = brand[0].strip()
        else:
            brand = ''
        if response.xpath("//div[@class='show-for-medium']//a//text()").extract():  # 跟卖数量
            sellers_num = response.xpath("//div[@class='show-for-medium']//a//text()").extract()
            re_1 = re.compile(r"\((\d+)\).*")
            sellers_num = re_1.findall(sellers_num[0])[0]
            # sellers_num = sellers_num[0]
        else:
            sellers_num = ''
        info = {
            'product_id': product_id,  # 产品id
            'product_url': product_url,  # 产品链接
            'images': images,  # 产品图片
            'title': title,  # 产品名称
            'keywords': keywords,  # 产品关键字
            'description': description,  # 商品描述
            'price': price,  # 产品价格
            'feedback': feedback,  # 反馈数
            'fba': fba,  # 是否为fba产品
            'starts': starts,  # 星级
            'revier': revier,  # 评论数
            'sellers_num': sellers_num,  # 跟卖数量
            'brand': brand,  # 品牌名
            'discount_price': discount_price,  # 折扣价
            'score': '0',  # 产品分数
            'operator': '0',  # 操作者
            'id': spider_id[0],
            'site': '2'

        }

        print(info)

        # item['souq_info'] = info
        #
        # yield item
