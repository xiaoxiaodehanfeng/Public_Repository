# -*- coding: utf-8 -*-
# @Time     : 2019/1/2/17:37
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_withdraw.py
# @Function : 测试取现接口

import unittest
import json
from ddt import ddt, data
from common.do_excel import DoExcel
from common import contants
from common.request import Request
from common.basic_data import DoRegex,Context
from datas.mysql_util import MysqlUtil


do_excel = DoExcel(file_name=contants.case_file)  # 实例化一个DoExcel对象
cases = do_excel.get_cases('withdraw')  # 返回一个case列表，由一个个Case对象/实例组成

@ddt
class TestWithdraw(unittest.TestCase):

    def setUp(self):
        self.sql = 'SELECT * FROM future.member WHERE MobilePhone = {0}'.format(Context.invest_user)
        self.mysql = MysqlUtil()
        # 取现前账户余额记录
        self.leaveamount_old = self.mysql.fetch_one(self.sql)['LeaveAmount']  # 获取账户余额---测试取现前的账户余额
        print("取现前的账户余额是：{}元".format(self.leaveamount_old))

    @data(*cases)
    def test_withdraw(self, case):
        data = DoRegex.replace(case.data)
        data = json.loads(data)
        # 先判断有没有cookies
        if hasattr(Context, 'cookies'):
            cookies = getattr(Context, 'cookies')   # 获取放到上下文里面的cookies
        else:
            cookies = None
        # 通过封装的Request类来完成接口的调用
        resp = Request(method=case.method, url=case.url, data=data, cookies=cookies)  # request请求时,data一定要是字典类型

        # 判断有没有cookies（有说明是登录接口）
        # --请求request拿到cookies --把cookies放到Context里
        if resp.get_cookies():    # 判断返回里面是否有cookies
            setattr(Context, 'cookies', resp.get_cookies())  # 放入到上下文中
        print("status_code：", resp.get_status_code())  # 打印响应码
        resp_dict = resp.get_json()  # 获取请求响应，字典
        self.assertEqual(case.expected, int(resp_dict['code']))  # 判断返回的code是否与期望结果一致

        # 完成数据库校验，判断取现成功之后账户余额增加正确，取现失败余额不变
        # 通过数据库查可以看到取现前的余额，取现后的余额，excel中的case.data可以查到取现金额amount
        # 数据库校验：期望的取现后的余额=取现前的余额-取现金额，实际的取现后的余额=查询数据库得到取现后的余额
        leaveamount_new = self.mysql.fetch_one(self.sql)['LeaveAmount']  # 再次获取账户余额---测试取现后的余额
        actual = float(leaveamount_new)  # 实际的账户余额 = 查询数据库得到账户的余额
        print("测试{}后的余额是：{}元".format(case.title, actual))
        if resp_dict['code'] == '10001' and resp_dict['msg'] == "取现成功":  # 取现请求后的响应码是10001并且取现成功
            amount = float(data['amount'])
            print('取现金额是：{}元'.format(amount))
            expected = float(self.leaveamount_old) - amount   # 取现成功，期望的账户余额=取现前的余额-取现金额
            self.assertEqual(expected, actual)  # 判断期望结果与实际结果是否一致
        elif resp_dict['code'] != '10001':
            expected = float(self.leaveamount_old)  # 取现失败，期望结果：账户余额不变，是取现前的余额
            self.assertEqual(expected, actual)      # 判断期望结果与实际结果是否一致

    def tearDown(self):
        self.mysql.close()


