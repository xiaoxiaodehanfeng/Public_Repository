# -*- coding: utf-8 -*-
# @Time     : 2018/12/24/7:25
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : mysql_util.py
# @Function : 

""""
1. 连接数据库
2. 编写一个sql
3. 建立游标
4. execute
"""
import pymysql
from common.config import CofigLoader

class MysqlUtil:

    def __init__(self):
        config = CofigLoader()
        host = config.get('mysql','host')
        port = config.getint('mysql','port')  # port是int类型
        user = config.get('mysql','user')
        password = config.get('mysql','password')
        # 建立连接，异常处理
        try:
            self.mysql = pymysql.connect(host=host, user=user, password=password,database=None,port=port,cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            raise e

    def fetch_one(self,sql):# 查询一条数据并返回
        cursor = self.mysql.cursor()  # 建立游标
        cursor.execute(sql)   # 根据sql执行查询
        return cursor.fetchone()

    def fetch_all(self,sql):# 查询多条条数据并返回
        cursor = self.mysql.cursor()  # 建立游标
        # 返回字典类型  可以更方便取值
        cursor.execute(sql)   # 根据sql执行查询
        return cursor.fetchall()

    def close(self):
        self.mysql.close()

if __name__ == '__main__':
    pass
    # sql = "select mobilephone from future.member where mobilephone != '' order by mobilephone desc limit 1;"
    # mysql_util = MysqlUtil()
    # results = mysql_util.fetch_one(sql)
    # max_mobile = results[0] # results: <class 'tuple'>  results[0]: <class 'str'>
    # print(max_mobile)
    # 数据库校验
    # print(type(results),results)  # {'mobilephone': '18999999882'}  返回字典
    # print(int(results['mobilephone'])+1)

    # sql2 = 'SELECT LeaveAmount FROM future.member WHERE MobilePhone = 13510563782;'
    # mysql_util = MysqlUtil()
    # results2 = mysql_util.fetch_one(sql2)
    # print(results2['LeaveAmount'])

    # mysql = MysqlUtil()
    # sql_1 = "select mobilephone from future.member where mobilephone != '' order by mobilephone desc limit 1;"
    # max_phone = mysql.fetch_one(sql_1)['mobilephone']
    # expected = int(max_phone) + 1
    # print(expected)
    #
    # sql_2 = 'select * from future.member where mobilephone = "{0}"'.format(max_phone)
    # member = mysql.fetch_one(sql_2)
    # print(member)
    # print(member['MobilePhone'])

    # mysql = MysqlUtil()
    # sql = 'select * from future.member where mobilephone = "13510563782" '
    # before_amount = mysql.fetch_one(sql)
    # print(before_amount)   # before_amount 字典类型

    mysql = MysqlUtil()
    # sql = "SELECT * FROM future.member;"
    # ID = mysql.fetch_one(sql)
    # print(ID, type(ID))

    sql_select_member = "SELECT * FROM future.member WHERE Id != '' ORDER BY Id ASC;"
    member_list = mysql.fetch_all(sql_select_member)
    print(member_list)
