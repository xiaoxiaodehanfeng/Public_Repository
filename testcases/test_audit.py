# -*- coding: utf-8 -*-
# @Time     : 2018/12/27/10:30
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_audit.py
# @Function : 测试审核接口

import unittest
import json
from common.do_excel import DoExcel
from common import contants
from common.request import Request
from ddt import ddt, data
from common.basic_data import DoRegex,Context
from datas.mysql_util import MysqlUtil


do_excel = DoExcel(file_name=contants.case_file)  # 实例化一个DoExcel对象
cases = do_excel.get_cases('audit')  # 返回一个case列表，由一个个Case对象/实例组成

@ddt
class TestAudit(unittest.TestCase):

    def setUp(self):
        self.mysql = MysqlUtil()
        self.sql = "SELECT * FROM future.loan WHERE Id != '' ORDER BY Id DESC LIMIT 1;"
        self.max_loan_id_old = self.mysql.fetch_one(self.sql)['Id']
        print("测试审核前的最大标的ID是：", self.max_loan_id_old)

    @data(*cases)  # 传进来cases列表
    def test_audit(self, case):  # 用case变量接收传进来的数据
        data = DoRegex.replace(case.data)  # 参数化处理
        data = json.loads(data)            # 将测试数据由字符串序列化成字典

        # 先判断有没有cookies
        if hasattr(Context, 'cookies'):            # 判断是否有cookies
            cookies = getattr(Context, 'cookies')  # 获取放到上下文里面的cookies
        else:
            cookies = None
        # Request封装类请求
        resp = Request(method=case.method, url=case.url, data=data, cookies=cookies)  # request请求时，data一定要是字典类型
        print("status_code：", resp.get_status_code())  # 打印响应码
        resp_dict = resp.get_json()  # 获取请求响应，字典
        # 优先判断响应返回的code是否与期望结果一致
        self.assertEqual(case.expected, int(resp_dict['code']))
        # 判断有没有cookies（有说明是登录接口）
        if resp.get_cookies():
            setattr(Context, 'cookies', resp.get_cookies())  # --请求request拿到cookies --把cookies放到Context里

        # 当创建标的成功时，根据借款人ID查看数据库loan表是否添加数据
        if resp_dict['msg'] == "加标成功":  # 新增标的成功的数据校验，判断数据库loan表有这条新增的数据
            # 再次查询数据库，获取最新的最大标的loan各项信息
            sql = "SELECT * FROM future.loan WHERE MemberID = {} ORDER BY Id DESC LIMIT 1;".format(Context.loan_member_id)
            loan = self.mysql.fetch_one(sql)  # loan是字典类型
            if loan is not None:   # 正常加标成功，不应该返回None,管理员加标成功的数据库校验
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
                # 将创建成功的标的ID写入到上下文中，用于之后投资用
                setattr(Context, 'loan_id', str(loan['Id']))  # 放一个str类型的进去，以备后面正则替换
            else:   # 返回None，表示数据库里面没有插入数据，管理员加标测试失败
                raise AssertionError

        # 当审核成功，需校验数据库loan表中status字段更改
        if case.url == '/loan/audit'and resp_dict['code'] == 10001:
            sql = 'SELECT * FROM future.loan WHERE MemberID = {} ORDER BY CreateTime DESC LIMIT 1;'.format(Context.loan_member_id)
            loan = self.mysql.fetch_one(sql)
            self.assertEqual(data['status'], loan['Status'])

        # 审核失败，数据库校验，审核前查询数据库，审核后查询，状态不变
        # 审核前查询的状态值放哪？
        # elif case.url == '/loan/audit'and resp_dict['code'] != 10001:
        #     sql = "SELECT * FROM future.loan WHERE Id = {};".format(data['id'])
        #     loan = self.mysql.fetch_one(sql)
        #     self.assertEqual(resp_dict, loan['Status'])

    def tearDown(self):
        self.mysql.close()


