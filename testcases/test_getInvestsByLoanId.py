# -*- coding: utf-8 -*-
# @Time     : 2019/1/4/18:16
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_getInvestsByLoanId.py
# @Function : 测试获取标的所有投资记录接口

import unittest
import json

from common.do_excel import DoExcel
from common import contants
from ddt import ddt, data
from datas.mysql_util import MysqlUtil
from common.basic_data import Context, DoRegex
from common.request import Request
from common.logger2 import MyLog

do_excel = DoExcel(file_name=contants.case_file)
cases = do_excel.get_cases(sheet_name='getInvestsByLoanId')

@ddt
class TestFetInvestsByLoanId(unittest.TestCase):

    def setUp(self):
        self.mysql = MysqlUtil()

    @data(*cases)
    def test_getInvestsByLoanId(self, case):
        data = DoRegex.replace(case.data)  # 参数化处理
        data = json.loads(data)  # 将测试数据由字符串序列化成字典

        if hasattr(Context, 'cookies'):  # 判断是否有cookies
            cookies = getattr(Context, 'cookies')  # 获取放到上下文里面的cookies
        else:
            cookies = None
        # Request封装类请求
        resp = Request(method=case.method, url=case.url, data=data, cookies=cookies)
        resp_dict = resp.get_json()  # 获取请求响应，字典
        # 判断返回里面是否有cookies(有说明是登录接口)
        if resp.get_cookies():  # 判断返回里面是否有cookies
            setattr(Context, 'cookies', resp.get_cookies())  # 放入到上下文中

        print("status_code：", resp.get_status_code())  # 打印响应码
        resp_dict = resp.get_json()  # 获取请求响应，字典
        self.assertEqual(case.expected, int(resp_dict['code']))  # 判断返回的code是否与期望结果一致

        # 数据库校验
        if resp_dict['msg'] == "获取记录成功":
            # 从数据库查invest表中某个标的/项目的全部投资记录
            sql_select_invest = "SELECT * FROM future.invest WHERE LoanId = {} ORDER BY Id DESC;".format(Context.invest_List_by_loan_id)
            invest_list = self.mysql.fetch_all(sql_select_invest)
            # 根据标的/项目ID获取invest表中某个标的/项目的投资记录的最大行数
            sql_select_row = "SELECT COUNT(Id) FROM future.invest WHERE LoanId = {};".format(Context.invest_List_by_loan_id)
            max_row = self.mysql.fetch_one(sql_select_row)['COUNT(Id)']

            if invest_list is not None:
                for i in range(0, max_row):  # 每一行数据校验
                    MyLog.info("正在校验第{}行数据".format(i))
                    # 判断请求返回的数据详情与数据库里面的详情是否一致
                    # 多个字段一致才assert通过
                    self.assertEqual(int(resp_dict['data'][i]['id']), invest_list[i]['Id'])
                    self.assertEqual(int(resp_dict['data'][i]['memberId']), invest_list[i]['MemberID'])
                    self.assertEqual(int(resp_dict['data'][i]['loanId']), invest_list[i]['LoanId'])
                    self.assertEqual(float(resp_dict['data'][i]['amount']), invest_list[i]['Amount'])
                    self.assertEqual(int(resp_dict['data'][i]['isValid']), invest_list[i]['IsValid'])
                    self.assertEqual(resp_dict['data'][i]['createTime'][0:19], invest_list[i]['CreateTime'].strftime("%Y-%m-%d %H:%M:%S"))
                    MyLog.info("校验结果：PASS")

    def tearDown(self):
        self.mysql.close()



