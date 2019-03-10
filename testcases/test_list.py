# -*- coding: utf-8 -*-
# @Time     : 2018/12/27/12:19
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_list.py
# @Function : 测试获取用户列表（list）接口

import json
import unittest
from common.do_excel import DoExcel
from common import contants
from ddt import ddt, data
from common.request import Request
from common.basic_data import DoRegex, Context
from datas.mysql_util import MysqlUtil

do_excel = DoExcel(file_name=contants.case_file)
cases = do_excel.get_cases(sheet_name='list')    # 返回cases列表

@ddt
class TestList(unittest.TestCase):

    def setUp(self):
        self.mysql = MysqlUtil()

    @data(*cases)
    def test_list(self, case):
        data = DoRegex.replace(case.data)
        data = json.loads(data)

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
        if resp_dict['msg'] == "获取用户列表成功":
            # 从数据库查到member表全部用户的信息
            # member_list是一个列表，列表是按照用户ID顺序排序。其中的元素是一个个字典。
            # resp_dict['data'] 也是一个列表，列表是按照用户ID顺序排序。其中的元素是一个个字典。
            sql_select_member = "SELECT * FROM future.member WHERE Id != '' ORDER BY Id ASC;"
            member_list = self.mysql.fetch_all(sql_select_member)
            # 获取member表最大行数
            sql_select_row = "SELECT COUNT(Id) FROM future.member;"
            max_row = self.mysql.fetch_one(sql_select_row)['COUNT(Id)']
            if member_list is not None:  # 如果从数据库里面查询出来不是空
                for i in range(0, max_row):  # 每一行数据校验
                    # 判断请求返回的数据详情与数据库里面的详情是否与一致
                    # 多个字段一致才assert通过
                    self.assertEqual(resp_dict['data'][i]['id'], member_list[i]['Id'])
                    self.assertEqual(resp_dict['data'][i]['mobilephone'], member_list[i]['MobilePhone'])
                    self.assertEqual(resp_dict['data'][i]['pwd'], member_list[i]['Pwd'])
                    self.assertEqual(resp_dict['data'][i]['regname'], member_list[i]['RegName'])
                    self.assertEqual(float(resp_dict['data'][i]['leaveamount']), float(member_list[i]['LeaveAmount']))
                    self.assertEqual(resp_dict['data'][i]['regtime'][0:19], member_list[i]['RegTime'].strftime("%Y-%m-%d %H:%M:%S"))
                    self.assertEqual(int(resp_dict['data'][i]['type']), member_list[i]['Type'])

    def tearDown(self):
        self.mysql.close()
