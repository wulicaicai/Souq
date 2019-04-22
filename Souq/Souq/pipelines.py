# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
import json, os, sys, time


class SouqPipeline(object):
    def process_item(self, item, spider):
        saudi = dict(item['souq_url_json'])
        souq_json = json.dumps(saudi)
        print(souq_json)
        type_name = requests.post(
            url='http://third.gets.com/api/index.php?act=insertSouqCategory&sec=20171212getscn',
            data=souq_json)
        print(type_name.text)
        return item

class SouqinfoPipeline(object):
    def process_item(self, item, spider):
        l=[]
        souq_info = item['souq_info']
        l.append(souq_info)
        souq_json1 = json.dumps(l)
        type_name = requests.post(
            url='http://third.gets.com/api/index.php?act=acceptSouqGoods&sec=20171212getscn',
            data=souq_json1)
        # print('数据已发送')
        print(type_name.text)
        return item
