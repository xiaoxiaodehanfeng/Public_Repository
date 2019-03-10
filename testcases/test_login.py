# -*- coding: utf-8 -*-
# @Time     : 2018/12/22/6:18
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : test_login.py
# @Function : 测试登录接口

'''1221作业
1.参数化excel登陆的测试数据，${register}
2.连接数据库，找到最大的手机号码并返回+1  # 从数据库找到的手机号放哪？
3.利用re模块来编写正则表达式查找变量${register}
4.把手机号替换上去  # 怎么取出来？
'''

import unittest
import json
from common.do_excel import DoExcel
from common import contants
from common.request import Request
from ddt import ddt,data
from common.basic_data import DoRegex
from common.config import CofigLoader
from common import logger


do_excel = DoExcel(file_name=contants.case_file)  # 实例化一个DoExcel对象
cases = do_excel.get_cases('login')  # 返回一个case列表，由一个个Case对象/实例组成

@ddt
class TestLogin(unittest.TestCase):

    def setUp(self):
        print("测试准备")

    # def test_login(self):
    #     do_excel = DoExcel(file_name=contants.case_file)  # 实例化一个DoExcel对象
    #     cases = do_excel.get_cases('login')  # 返回一个case列表，由一个个Case对象/实例组成
    #     for case in cases:
    #         data = json.loads(case.data)   # 从excel中取到的data是一个字符串，把字符串转为字典
    #         resp = Request(method=case.method,url=case.url,data=data)
    #         print("status_code：", resp.get_status_code())  # 打印响应码
    #         resp_dict = resp.get_json()  # 获取请求响应，字典
    #         print("resp_dict ：", resp_dict)
    #         self.assertEqual(case.expected,resp.get_text())  # text???json????

    """拓展：file_data测试方法装饰器，读取文件数据（json/yaml），parameterized模块"""

    @data(*cases)  # 传进来cases列表
    def test_login(self, case):  # 用case变量接收传进来的数据
        # 在这里写一个正则表达式，查找到手机号,密码，并替换掉excel中的参数
        if case.case_id == 1:  # 判断是否需要进行参数化
            do_regex = DoRegex()
            case.data = do_regex.replace(case.data)
        data = json.loads(case.data)  # 从excel中取到的data是一个字符串，把字符串转为字典

        # 也可以不用正则，取出case.data字典里的手机号，直接赋值替换
        # data = json.loads(case.data)  # 从excel中取到的data是一个字符串，loads() 把字符串序列化为字典
        # if data['mobilephone'] == '${invest_user}':  # 判断是否需要进行参数化
        #     config = CofigLoader()
        #     data['mobilephone'] = config.get('basic','invest_user')  # 赋值替换excel中的手机号
        #     data['pwd'] = config.get('basic','invest_pwd')

        resp = Request(method=case.method, url=case.url, data=data)
        print("status_code：", resp.get_status_code())  # 打印响应码
        resp_dict = resp.get_json()  # 获取请求响应，字典
        # print(resp_dict)
        logger.my_logger.info('测试用例名称：{0}'.format(case.title))
        logger.my_logger.info('测试用例数据：{0}'.format(case.data))
        try:
            self.assertEqual(case.expected, resp.get_text())
            print("测试通过")
        except AssertionError as e:
            print('测试失败')

        # 测试结果写入excel中
        if case.expected == resp.get_text():
            print("此次测试PASS")
            do_excel.write_back_by_case_id(sheet_name='login', case_id=case.case_id, actual=resp.get_text(),result='PASS')
        else:
            print("此次测试FAIL")
            do_excel.write_back_by_case_id(sheet_name='login', case_id=case.case_id, actual=resp.get_text(),result='FAIL')

    def tearDown(self):
        print("测试清除")
