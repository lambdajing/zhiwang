#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/29 0029 10:25
# @Author  : lijing
# @FileName: 知网4.py
import requests
import time
import urllib3
from save_result import MysqlUtil
from lxml import etree
urllib3.disable_warnings()

class ZhiWangSpider(object):

    def __init__(self, school_name, pages):
        self.headers = {'Host': 'kns.cnki.net',
                        'Sec-Fetch-Mode': 'nested-navigate',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Connection': 'keep-alive',
                        }
        self.url = 'https://kns.cnki.net/kns/brief/brief.aspx?'
        self.session = requests.session()
        self.session = requests.session()
        self.session.headers = self.headers
        self.session.verify = False
        self.school_name = school_name
        self.pages = pages
        self.mysql = MysqlUtil()

    def get_cookies(self):
        params = {
            'action': 'Recommend_tip',
            'kw': self.school_name,
            'dbcode': 'SCDB',
            'selectedField': '主题',
            'valueFiled': 'SU$%=|,KY$=|,TI$%=|,FT$%=|,AU$=|,AF$%,AB$%=|,RF$%=|,CLC$=|??,LY$%=|,',
            '__': '',
        }
        self.session.get('https://kns.cnki.net/kns/Request/GetAptitude_searchHandler.ashx?', params=params)
        # 第一个请求
        t = time.time()
        now_time = int(round(t * 1000))
        params = {
            'keyword': self.school_name,
            'td': now_time,
        }
        self.session.get('https://kns.cnki.net/CRRS//RelItems.ashx?', params=params)
        data = {'action': '',
                'ua': '1.11',
                'isinEn': '1',
                'PageName': 'ASP.brief_default_result_aspx',
                'DbPrefix': 'SCDB',
                'DbCatalog': '中国学术文献网络出版总库',
                'ConfigFile': 'SCDBINDEX.xml',
                'db_opt': 'CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD',
                'txt_1_sel': 'SU$%=|',
                'txt_1_value1': self.school_name,
                'txt_1_special1': '%',
                'his': '0',
                'parentdb': 'SCDB',
                '__': '',
                }
        self.session.post('https://kns.cnki.net/kns/request/SearchHandler.ashx', data=data)
        # birf 此时就是可以获取完整数据的url
        t1 = time.time()
        now_time1 = int(round(t1 * 1000))
        params = {
            'pagename': "ASP.brief_default_result_aspx",
            'isinEn': 1,
            'dbPrefix': 'SCDB',
            'dbCatalog': '中国学术文献网络出版总库',
            'ConfigFile': 'SCDBINDEX.xml',
            'research': 'off',
            't': now_time1,
            'keyValue': self.school_name,
            'S': 1,
            'sorttype': "",
        }
        return self.session.get(self.url, params=params)

    @staticmethod
    def get_html_str(response):
        return response.content.decode()

    def iter_pages(self, pages):
        params = {
            'curpage': pages,
            'RecordsPerPage': '20',
            'QueryID': '0',
            'ID': '',
            'turnpage': '1',
            'tpagemode': 'L',
            'dbPrefix': 'SCDB',
            'Fields': '',
            'DisplayMode': 'listmode',
            'PageName': 'ASP.brief_default_result_aspx',
            'isinEn': '1',
        }
        return self.session.get(self.url, params=params)

    @staticmethod
    def parse_html(html):
        html_str = etree.HTML(html)
        tr_list = html_str.xpath('//table[@class="GridTableContent"]//tr[@bgcolor]')
        result_list = []
        for tr in tr_list:
            item = {}
            title = tr.xpath(r'.//td/a[@class="fz14"]//text()')
            author = tr.xpath(r'.//td/a[@class="KnowledgeNetLink"]/text()')
            refer = tr.xpath(r'.//td[4]/a[@target="_blank"]/text()')
            push_date = tr.xpath('.//td[@align="center"][1]/text()')
            types = tr.xpath(r'.//td[@align="center"][2]/text()')
            recommend_times = tr.xpath(r'.//td[@align="right"]/span/a[@class="KnowledgeNetLink"]/text()')
            download_times = tr.xpath(r'.//td[@align="center"][3]/span[@class="downloadCount"]/a/text()')
            item["author"] = " ".join(author).strip() if author else ""
            item["title"] = "".join(title).strip() if title else ""
            item["refer"] = refer[0].strip() if refer else ""
            item["push_date"] = push_date[0].strip() if push_date else None
            item["type"] = types[0].strip() if types else ""
            item["recommend_times"] = recommend_times[0].strip() if recommend_times else 0
            item["download_times"] = download_times[0].strip() if download_times else 0
            result_list.append(item)
        return result_list

    # 存到本地数据库mysql
    def save_result(self, result_list):
        self.mysql.insert(result_list)

    def run(self):
        resp = self.get_cookies()
        html_str = self.get_html_str(resp)
        result_list = self.parse_html(html_str)
        self.save_result(result_list)
        for i in range(2, self.pages+1):
            resp = self.iter_pages(i)
            result_list = self.parse_html(resp.content.decode())
            self.save_result(result_list)


if __name__ == '__main__':
    zhi_wang = ZhiWangSpider("安阳工学院", 7)
    zhi_wang.run()
