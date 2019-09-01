#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/28 0028 22:27
# @Author  : lijing
# @FileName: utils.py

text = """action:
ua: 1.11
isinEn: 1
PageName: ASP.brief_default_result_aspx
DbPrefix: SCDB
DbCatalog: 中国学术文献网络出版总库
ConfigFile: SCDBINDEX.xml
db_opt: CJFQ,CDFD,CMFD,CPFD,IPFD,CCND,CCJD
txt_1_sel: SU$%=|
txt_1_value1: 安阳工学院
txt_1_special1: %
his: 0
parentdb: SCDB
__: Wed Aug 28 2019 22:25:15 GMT+0800 (中国标准时间)"""


@staticmethod
def get_form_data(data: str):
    return {i.split(":")[0].strip(): i.split(":")[1].strip() for i in data.splitlines()}


if __name__ == '__main__':
    print(get_form_data(text))
