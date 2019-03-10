# -*- coding: utf-8 -*-
# @Time     : 2018/12/29/20:04
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_add.py
# @Function : 测试新增标的接口

# 1.管理员登录 2.管理员新增标的--其中memberId是借款人的ID

import unittest
import json
from ddt import ddt, data
from common.do_excel import DoExcel
from common import contants
from common.request import Request
from common.basic_data import DoRegex, Context
from datas.mysql_util import MysqlUtil

do_excel = DoExcel(file_name=contants.case_file)
cases = do_excel.get_cases('add')

@ddt
class TestAdd(unittest.TestCase):

    def setUp(self):
        self.mysql = MysqlUtil()
        self.sql = "SELECT * FROM future.loan WHERE Id != '' ORDER BY Id DESC LIMIT 1;"
        self.max_loan_id_old = self.mysql.fetch_one(self.sql)['Id']
        print("测试加标前的最大标的ID是：", self.max_loan_id_old)

    @data(*cases)
    def test_add(self, case):
        data = DoRegex.replace(case.data)  # 通过正则取excel的数据，Context覆盖excel的数据
        data = json.loads(data)            # 从excel中取到的data是一个字符串，loads()把字符串序列化为字典
        # --请求request拿到cookies
        # 先判断有没有cookies
        if hasattr(Context, 'cookies'):
            cookies = getattr(Context, 'cookies')   # 获取放到上下文里面的cookies
        else:
            cookies = None
        # 通过封装的Request类来完成接口的调用
        resp = Request(method=case.method, url=case.url, data=data, cookies=cookies)  # request请求时,data一定要是字典类型
        # 判断有没有cookies（有说明是登录接口）
        if resp.get_cookies():   # 判断返回里面是否有cookies
            setattr(Context, 'cookies', resp.get_cookies())  # 放入到上下文中
        print("status_code：", resp.get_status_code())  # 打印响应码
        resp_dict = resp.get_json()   # 获取请求响应，字典
        self.assertEqual(case.expected, int(resp_dict['code']))   # 判断返回的code是否与期望结果一致
        # 完成数据库校验
        # 再次查询数据库，获取最新的最大标的loan各项信息
        sql = "SELECT * FROM future.loan WHERE MemberID = {} ORDER BY Id DESC LIMIT 1;".format(Context.loan_member_id)
        loan = self.mysql.fetch_one(sql)  # loan是字典类型
        if resp_dict['msg'] == "加标成功":  # 新增标的成功的数据校验，判断数据库loan表有这条新增的数据
            if loan is not None:   # 正常加标成功，不应该返回None
                max_loan_id_new = self.max_loan_id_old + 1
                expected = max_loan_id_new   # 期望结果：测试加标成功前的最大标的ID加上1
                # 判断数据库里面的标的详情是否与测试数据一致
                # 多个字段一致才assert通过
                self.assertEqual(expected, loan['Id'])  # 实际结果：数据库查询的最大标的ID
                self.assertEqual(int(data['memberId']), loan['MemberID'])  # MemberID是借款人的ID，管理员登录进行操作
                self.assertEqual(float(data['amount']), loan['Amount'])
                self.assertEqual(data['title'], loan['Title'])
                self.assertEqual(float(data['loanRate']), loan['LoanRate'])
                self.assertEqual(data['loanTerm'], loan['LoanTerm'])
                self.assertEqual(data['loanDateType'], loan['LoanDateType'])
                self.assertEqual(data['repaymemtWay'], loan['RepaymemtWay'])
                self.assertEqual(data['biddingDays'], loan['BiddingDays'])
                self.assertEqual(1, loan['Status'])
                print("测试加标后的最大标的ID是：", max_loan_id_new)
            else:   # 返回None，表示数据库里面没有插入数据，管理员加标测试失败
                raise AssertionError
        elif resp_dict['code'] != '10001':
            expected = self.max_loan_id_old   # 期望结果：测试加标成功前的最大标的ID
            self.assertEqual(expected, loan['Id'])

    def tearDown(self):
        self.mysql.close()
