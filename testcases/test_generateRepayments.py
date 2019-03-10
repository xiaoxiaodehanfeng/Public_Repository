# -*- coding: utf-8 -*-
# @Time     : 2019/1/4/16:19
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_generateRepayments.py
# @Function : 测试生成回款计划

# 管理员登录--管理员加标--管理员审核
# 投资人登录--投资人投资竞标--直到标满标的状态自动变为核保审批状态    # 每投资一次，invest表会新增一条记录，根据LoanId查看
# 投资人登录--生成回款计划（）   # 一条投资记录，会生成一条或多条回款计划记录,根据invest表的ID，查看回款计划

import unittest
import json

from common.do_excel import DoExcel
from common import contants
from ddt import ddt, data
from datas.mysql_util import MysqlUtil
from common.basic_data import Context, DoRegex
from common.request import Request

do_excel = DoExcel(file_name=contants.case_file)
cases = do_excel.get_cases(sheet_name='generateRepayments')

@ddt
class TestGenerateRepayments(unittest.TestCase):

    def setUp(self):
        pass

    @data(*cases)
    def test_generateRepayments(self, case):
        data = DoRegex.replace(case.data)  # 参数化处理
        data = json.loads(data)            # 将测试数据由字符串序列化成字典

        if hasattr(Context, 'cookies'):  # 判断是否有cookies
            cookies = getattr(Context, 'cookies')  # 获取放到上下文里面的cookies
        else:
            cookies = None
        # Request封装类请求
        resp = Request(method=case.method, url=case.url, data=data, cookies=cookies)
        print(resp.get_text())
        resp_dict = resp.get_json()  # 获取请求响应，字典
        # 优先判断响应返回的code是否与期望结果一致
        self.assertEqual(case.expected, int(resp_dict['code']))
        # 判断有没有cookies
        if resp.get_cookies():  # 判断返回里面是否有cookies
            setattr(Context, 'cookies', resp.get_cookies())  # 放入到上下文中

        # 数据库校验
        pass

    def tearDown(self):
        pass
