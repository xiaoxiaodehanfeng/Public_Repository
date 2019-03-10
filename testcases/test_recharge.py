# -*- coding: utf-8 -*-
# @Time     : 2018/12/24/21:02
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_recharge.py
# @Function : 测试充值接口

""" 完整的充值过程：
--获取期望结果（把leaveamount放到setUp里面，定义一个global变量）
--从配置文件取到基础数据
--放到Context的属性
--通过正则取excel的数据，Context覆盖excel的数据
--请求request拿到cookies
--把cookies放到Context里
--请求充值
--取出context里的cookies
--进行充值
--数据校验（取出来期望结果，查询数据库leaveamount，两个比较）"""

import unittest
import json
from common.do_excel import DoExcel
from common import contants
from common.request import Request
from ddt import ddt,data
from common.basic_data import DoRegex, Context
from datas.mysql_util import MysqlUtil
from common.logger2 import MyLog

"""执行用例时，把从excel取到的数据，通过正则解析出来，再通过setattar() 放到Context的属性里，保存。
使用时通过getattr()取出来使用。"""

do_excel = DoExcel(file_name=contants.case_file)  # 实例化一个DoExcel对象
cases = do_excel.get_cases('recharge')  # 返回一个case列表，由一个个Case对象/实例组成

sql = 'SELECT LeaveAmount FROM future.member WHERE MobilePhone = {0}'.format(Context.invest_user)
mysql = MysqlUtil()

@ddt
class TestRecharge(unittest.TestCase):
    # 在setup里面完成充值前账户余额的获取
    def setUp(self):
        # 充值前账户余额记录
        self.leaveamount_old = mysql.fetch_one(sql)  # 获取账户余额---测试充值前的账户余额
        MyLog.info("充值前的余额是：{}元".format(self.leaveamount_old['LeaveAmount']))

        # 查询投资用户的账户信息
        # self.sql = 'select * from future.member where mobilephone = {0}'.format(Context.invest_user)
        # self.before_amount = self.mysql.fetch_one(self.sql)['LeaveAmount']  # 账户余额
        # print("充值前的金额", self.before_amount)

    @data(*cases)  # 传进来cases列表
    def test_recharge(self, case):  # 用case变量接收传进来的数据
        # 参数化处理
        data = DoRegex.replace(case.data)  # 通过正则取excel的数据，Context覆盖excel的数据
        data = json.loads(data)            # 从excel中取到的data是一个字符串，loads()把字符串序列化为字典
        MyLog.info("正在执行第{}条用例：{}。".format(case.case_id, case.title))
        MyLog.info("测试数据是{}".format(data))
        # --请求request拿到cookies
        #         # 先判断有没有cookies
        if hasattr(Context, 'cookies'):
            cookies = getattr(Context, 'cookies')   # 获取放到上下文里面的cookies
        else:
            cookies = None
        # 通过封装的Request类来完成接口的调用
        resp = Request(method=case.method, url=case.url, data=data, cookies=cookies)  # request请求时,data一定要是字典类型
        # 判断有没有cookies（有说明是登录接口）
        # --请求request拿到cookies --把cookies放到Context里
        # if resp.get_cookies('JSESSIONID'):
            # setattr(Context,'cookies',{'JSESSIONID':resp.get_cookies('JSESSIONID')})
        if resp.get_cookies():  # 判断返回里面是否有cookies
            setattr(Context, 'cookies', resp.get_cookies())  # 放入到上下文中
        print("status_code：", resp.get_status_code())  # 打印响应码
        resp_dict = resp.get_json()  # 获取请求响应，字典
        self.assertEqual(case.expected, int(resp_dict['code']))  # 判断返回的code是否与期望结果一致

        # 完成数据库校验，判断充值成功之后账户余额增加正确，充值失败余额不变
        # 通过数据库查可以看到充值前的余额，充值后的余额，excel中的case.data可以查到充值金额amount
        # 数据库校验：期望的充值后的余额=充值金额+充值前的余额，实际的充值后的余额=查询数据库得到充值后的余额
        leaveamount_new = mysql.fetch_one(sql)  # 再次获取账户余额---测试充值后的余额
        actual = float(leaveamount_new['LeaveAmount'])  # 实际的账户余额 = 查询数据库得到账户的余额
        MyLog.info("测试{}后的余额是：{}元".format(case.title, actual))
        if resp_dict['code'] == '10001' and resp_dict['msg'] == "充值成功":  # 充值请求后的响应码是10001并且充值成功
            amount = float(data['amount'])  # 通过excel中的case.data可以查到充值金额amount
            MyLog.info('充值金额是：{}元'.format(amount))
            expected = float(self.leaveamount_old['LeaveAmount']) + amount  # 充值成功，期望的账户余额=充值前的余额+充值金额
            self.assertEqual(expected, actual)  # 判断期望结果与实际结果是否一致
            MyLog.info("此次测试结果是：PASS")
        elif resp_dict['code'] != '10001':
            expected = float(self.leaveamount_old['LeaveAmount'])   # 充值失败，期望结果：账户余额不变，是充值前的余额
            self.assertEqual(expected, actual)                      # 判断期望结果与实际结果是否一致
            MyLog.info("此次测试结果是：PASS")

        # 用户余额有变动的话，会在资金流水表插入一条记录 流水记录接口验证---再补充!

    def tearDown(self):
        pass






