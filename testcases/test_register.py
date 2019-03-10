# -*- coding: utf-8 -*-
# @Time     : 2018/12/31/14:19
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_register.py
# @Function : 测试注册接口

"""
1. 从数据库找到最大手机号+1 -- 放哪里？
2. 新的手机号替换excel中的手机号
3. request请求
5. 数据验证
6. 报告
"""
# 参数化，数据库校验

import unittest
import re
import json
from common.do_excel import DoExcel
from common import contants
from common.request import Request
from ddt import ddt,data
from datas.mysql_util import MysqlUtil

do_excel = DoExcel(file_name=contants.case_file)  # 实例化一个DoExcel对象
cases = do_excel.get_cases('register')  # 返回一个case列表，由一个个Case对象/实例组成


@ddt
class TestRegister(unittest.TestCase):

    # 每次运行只执行一次的操作，放到setUpClass里面，不放到setUp里。
    @classmethod
    def setUpClass(cls):
        global mysql
        mysql = MysqlUtil()
        sql = "select mobilephone from future.member where mobilephone != '' order by mobilephone desc limit 1;"
        global max_phone_old
        max_phone_old = mysql.fetch_one(sql)['mobilephone']

    @data(*cases)
    def test_register(self,case):
        # 使用正则，首先从数据库查找到最大手机号加1，通过正则替换excel中的参数---还需再改！！！
        # if case.case_id == 1:
        #     # 从数据库找到最大手机号+1
        #     max_phone_old = mysql.fetch_one(sql)['mobilephone']
        #     max_phone = int(max_phone_old) + 1
        #     print("最大手机号是：",max_phone)
        #     # 新的手机号替换excel中的手机号
        #     phone = re.findall(pattern='\d{11}', string=case.data)[0]    # 先从excel中取出手机号
        #     case.data = case.data.replace(phone,str(max_phone))  # replace替换

        # 也可以不用正则，取出case.data字典里的手机号，直接赋值替换
        data = json.loads(case.data)  # 从excel中取到的data是一个字符串，loads() 把字符串序列化为字典
        if data['mobilephone'] == '${register}':     # 判断是否需要进行参数化
            max_phone_new = int(max_phone_old) + 1   # 取到数据库里面最大的手机号码，进行加1
            data['mobilephone'] = max_phone_new     # 赋值替换excel中的手机号

        resp = Request(method=case.method, url=case.url, data=data)  # request请求时，data一定要是字典类型
        print("status_code：", resp.get_status_code())  # 打印响应码
        resp_dict = resp.get_json()  # 获取请求响应，字典
        self.assertEqual(case.expected, resp.get_text())

        # 数据库校验
        if resp_dict['code'] == 10001:  # 注册成功的数据校验，判断数据库member表有这条数据
            sql = 'select * from future.member where mobilephone = "{0}"'.format(max_phone_new)
            member = self.mysql.fetch_one(sql)   # member是字典类型
            expected = max_phone_new
            if member is not None:  # 正常注册成功，不应该返回None
                self.assertEqual(expected, member['mobilephone'])
            else:         # 返回None，代表注册成功之后但是数据库里面没有插入数据
                print("注册失败，数据库没有插入数据")
        # else:   # 注册失败的数据校验，判断数据库member表没有这条数据--继续改。。。
        #     sql_3 = 'select * from future.member '
        #     member = mysql.fetch_one(sql_3)  # member是字典类型
        #     self.assertEqual(None, member)

        # 注册失败可以不做数据库校验，也可以验证没有插入,返回的是None
        # 有的手机号已被注册，excel中注册失败的手机号是已被注册过的，数据库有这条数据，怎么校验注册失败？？？

        # 测试结果写入excel中--还要改！
        # if case.expected == resp.get_text():
        #     print("此次测试PASS")
        #     do_excel.write_back_by_case_id(sheet_name='register2',case_id=case.case_id,actual=resp.get_get_text(),result='PASS')
        # else:
        #     print("此次测试FAIL")
        #     do_excel.write_back_by_case_id(sheet_name='register2', case_id=case.case_id, actual=resp.get_text(),result='FAIL')

    @classmethod
    def tearDownClass(cls):
        mysql.close()

