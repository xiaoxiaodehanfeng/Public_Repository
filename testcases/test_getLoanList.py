# -*- coding: utf-8 -*-
# @Time     : 2019/1/4/14:23
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_getLoanList.py
# @Function : 测试获取表列表接口

import unittest
from ddt import ddt, data
import json
from common.do_excel import DoExcel
from common import contants
from common.request import Request
from common.basic_data import DoRegex, Context
from datas.mysql_util import MysqlUtil
from common.logger2 import MyLog

do_excel = DoExcel(file_name=contants.case_file)
cases = do_excel.get_cases(sheet_name='getLoanList')    # 返回cases列表

@ddt
class TestGetLoanList(unittest.TestCase):

    def setUp(self):
        self.mysql = MysqlUtil()

    @data(*cases)
    def test_getLoanList(self, case):
        data = DoRegex.replace(case.data)  # 参数化处理
        data = json.loads(data)            # 字符串序列化为字典
        # 先判断有没有cookies
        if hasattr(Context, 'cookies'):
            cookies = getattr(Context, 'cookies')
        else:
            cookies = None
        # 通过封装的Request类来完成接口的调用
        resp = Request(method=case.method, url=case.url, data=data, cookies=cookies)
        # 判断返回里面是否有cookies(有说明是登录接口)
        if resp.get_cookies():
            setattr(Context, 'cookies', resp.get_cookies())  # cookies放入到上下文中
        print("status_code：", resp.get_status_code())  # 打印响应码
        resp_dict = resp.get_json()  # 获取请求响应，字典
        self.assertEqual(case.expected, int(resp_dict['code']))  # 判断返回的code是否与期望结果一致

        # 完成数据库校验
        if resp_dict['msg'] == "获取标列表成功":
            # 从数据库查到loan表全部标的信息
            # loan_list是一个列表，列表是按照标的ID顺序排序。其中的元素是一个个字典。
            # resp_dict['data'] 也是一个列表，列表是按照标的ID顺序排序。其中的元素是一个个字典。
            sql_select_loan = "SELECT * FROM future.loan WHERE Id != '' ORDER BY Id ASC;"
            loan_list = self.mysql.fetch_all(sql_select_loan)
            # 获取loan表最大行数
            sql_select_row = "SELECT COUNT(Id) FROM future.loan;"
            max_row = self.mysql.fetch_one(sql_select_row)['COUNT(Id)']
            if loan_list is not None:  # 如果从数据库里面查询出来不是空
                for i in range(0, max_row):  # 每一行数据校验
                    # 判断数据库里面的标的详情是否与请求返回的数据详情一致
                    # 多个字段一致才assert通过
                    self.assertEqual(int(resp_dict['data'][i]['id']), loan_list[i]['Id'])
                    self.assertEqual(int(resp_dict['data'][i]['memberId']), loan_list[i]['MemberID'])
                    self.assertEqual(resp_dict['data'][i]['title'], loan_list[i]['Title'])
                    self.assertEqual(float(resp_dict['data'][i]['amount']), float(loan_list[i]['Amount']))
                    self.assertEqual(float(resp_dict['data'][i]['loanRate']), float(loan_list[i]['LoanRate']))
                    self.assertEqual(int(resp_dict['data'][i]['loanTerm']), loan_list[i]['LoanTerm'])
                    self.assertEqual(int(resp_dict['data'][i]['loanDateType']), loan_list[i]['LoanDateType'])
                    self.assertEqual(int(resp_dict['data'][i]['repaymemtWay']), loan_list[i]['RepaymemtWay'])
                    self.assertEqual(int(resp_dict['data'][i]['biddingDays']), loan_list[i]['BiddingDays'])
                    self.assertEqual(int(resp_dict['data'][i]['status']), loan_list[i]['Status'])
                    self.assertEqual(resp_dict['data'][i]['createTime'][0:19], loan_list[i]['CreateTime'].strftime("%Y-%m-%d %H:%M:%S"))
                    # 时间是空值时，怎么校验？？？
                    # self.assertEqual(resp_dict['data'][i]['biddingStartTime'][0:19], loan_list[i]['BiddingStartTime'].strftime("%Y-%m-%d %H:%M:%S"))
                    # self.assertEqual(resp_dict['data'][i]['fullTime'][0:19],loan_list[i]['FullTime'].strftime("%Y-%m-%d %H:%M:%S"))
                    MyLog.info("正在校验数据库第{}行数据，结果：PASS".format(i+1))

    def tearDown(self):
        self.mysql.close()
