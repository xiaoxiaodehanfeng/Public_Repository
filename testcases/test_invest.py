# -*- coding: utf-8 -*-
# @Time     : 2018/12/27/11:45
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_invest.py
# @Function : 测试投资竞标接口

# 管理员 -- 登录 -- 加标 -- 审核
# 投资人 -- 登录 -- 充值 -- 投资

# 登录 -- 获取cookies -- 测试没有cookies

# 一个标的/项目，有多个用户投资，所以会生成多条投资记录
# 用户每投资一次，就生成一条投资记录
# 用户余额有变动的话，会在资金流水表插入一条记录

import unittest
import json

from common.do_excel import DoExcel
from common import contants
from ddt import ddt, data
from datas.mysql_util import MysqlUtil
from common.basic_data import Context, DoRegex
from common.request import Request


do_excel = DoExcel(file_name=contants.case_file)
cases = do_excel.get_cases(sheet_name='invest')

@ddt
class TestInvest(unittest.TestCase):

    def setUp(self):
        self.mysql = MysqlUtil()
        self.sql_select_member = 'SELECT * FROM future.member WHERE MobilePhone = {0}'.format(Context.invest_user)
        # 投资竞标前的账户余额
        self.leaveamount_old = self.mysql.fetch_one(self.sql_select_member)['LeaveAmount']  # 获取账户余额---测试投资竞标前的账户余额
        print("投资竞标前的投资人账户余额是：{}元".format(self.leaveamount_old))

    @data(*cases)
    def test_invest(self, case):
        data = DoRegex.replace(case.data)  # 参数化处理
        data = json.loads(data)            # 将测试数据由字符串序列化成字典

        if hasattr(Context, 'cookies'):            # 判断是否有cookies
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

        # 当创建标的成功时，根据借款人ID查看数据库loan表是否添加数据
        if resp_dict['msg'] == '加标成功':
            sql_select_loan = 'SELECT * FROM future.loan WHERE MemberID = {} ORDER BY CreateTime DESC LIMIT 1;'.format(Context.loan_member_id)
            loan = self.mysql.fetch_one(sql_select_loan)
            # 管理员加标成功的数据库校验
            if loan is not None:   # 如果从数据库里面查询出来不是空，则创建标的成功
                # 判断数据库里面的标的详情是否与测试数据一致
                # 多个字段一致才assert通过
                self.assertEqual(int(data['memberId']), loan['MemberID'])  # MemberID是借款人的ID，管理员操作
                self.assertEqual(float(data['amount']), loan['Amount'])
                self.assertEqual(data['title'], loan['Title'])
                self.assertEqual(float(data['loanRate']), loan['LoanRate'])
                self.assertEqual(data['loanTerm'], loan['LoanTerm'])
                self.assertEqual(data['loanDateType'], loan['LoanDateType'])
                self.assertEqual(data['repaymemtWay'], loan['RepaymemtWay'])
                self.assertEqual(data['biddingDays'], loan['BiddingDays'])
                # 将创建成功的标的ID写入到上下文中，用于之后投资用
                setattr(Context, 'loan_id', str(loan['Id']))    # 放一个str类型的进去，以备后面正则替换
            else:    # 如果数据库里面没有数据，则管理员加标测试失败
                raise AssertionError

        # 当审核成功，需校验数据库loan表中status字段更改
        if resp_dict['msg'] == "更新状态成功：竞标开始，当前标为竞标中状态":
            sql_select_loan = 'SELECT * FROM future.loan WHERE MemberID = {} ORDER BY CreateTime DESC LIMIT 1;'.format(Context.loan_member_id)
            loan = self.mysql.fetch_one(sql_select_loan)
            self.assertEqual(data['status'], loan['Status'])

        # 当投资成功时，根据投资人ID查看数据member表中验证余额是否减少
        if resp_dict['msg'] == "竞标成功":
                amount = float(data['amount'])  # 投资金额
                print('投资竞标金额是：{}元'.format(amount))
                leaveamount_new = self.mysql.fetch_one(self.sql_select_member)['LeaveAmount']  # 投资后的金额
                actual = float(leaveamount_new)
                expected = float(self.leaveamount_old) - float(amount)  # 期望结果 = 投资前的余额 - 投资金额
                self.assertEqual(expected, actual)
                print("测试{}后的账户余额是：{}元".format(case.title, float(actual)))
        elif resp_dict['code'] != '10001':  # 投资失败，余额不变
                leaveamount_new = self.mysql.fetch_one(self.sql_select_member)['LeaveAmount']  # 投资后的金额
                actual = leaveamount_new
                print("测试{}后的账户余额是：{}元".format(case.title, float(actual)))
                expected = self.leaveamount_old   # 期望结果 = 投资前的余额
                self.assertEqual(expected, actual)
        # 当投资成功时，根据标的ID查看invest表，每投资一次，验证invest表新增一条记录---再补充!
        pass

        # 用户余额有变动的话，会在资金流水表插入一条记录 ---再补充!
        pass

    def tearDown(self):
        self.mysql.close()
