#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/8/29 0029 21:50
# @Author  : lijing
# @FileName: save_result.py

import pymysql
import traceback
from DBUtils.PooledDB import PooledDB
from pymysql.cursors import DictCursor


class MysqlUtil():

    def __init__(self):
        self.pool = self.get_connection_pool(5)

    def get_connection_pool(self, maxconnections):
        pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=maxconnections,  # 连接池允许的最大连接数，0和None表示不限制连接数
            # mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            # maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
            # maxshared=3,  # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            # blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            # maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            # setsession=[],  # 开始会话前执行的命令列表。
            # ping=0,
            # # ping MySQL服务端，检查是否服务可用。
            host='127.0.0.1',
            port=3306,
            user='root',
            password='mysql',
            database='zhiwang',
            charset='utf8'
        )
        return pool

    def insert(self, item_list):
        item_list = [list(i.values()) + list(i.values())[-2:] for i in item_list]
        connection = self.pool.connection()
        cursor = connection.cursor()
        for item in item_list:
            try:
                sql = 'insert into zhiwang_result(author,title,refer,push_date,types,recommend_times,download_times) values(%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE recommend_times=%s,download_times=%s'
                cursor.execute(sql, item)
                connection.commit()
            except Exception as e:
                traceback.print_exc()
                connection.rollback()  # 插入出错，回滚
        else:
            cursor.close()
            connection.close()


if __name__ == '__main__':
    pass
