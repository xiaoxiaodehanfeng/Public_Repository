# -*- coding: utf-8 -*-
# @Time     : 2018/12/21/10:15
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : contants.py
# @Function : 常量管理 不会改变的变量

import os

# p1 = os.path.abspath(__file__)
# print(p1)  # D:\Project\MOOC\Lemon\Hester_Python12_API\common\contants.py
# p2 = os.path.dirname(p1)
# print(p2)  # D:\Project\MOOC\Lemon\Hester_Python12_API\common
# p3 = os.path.dirname(p2)
# print(p3)  # D:\Project\MOOC\Lemon\Hester_Python12_API

# 项目根路径
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# configs文件夹路径
configs_dir = os.path.join(base_dir, 'configs')

# datas文件夹路径
datas_dir = os.path.join(base_dir, 'datas')
case_file = os.path.join(datas_dir, 'cases_v2.xlsx')
# logs文件夹路径
logs_dir = os.path.join(base_dir, 'logs')

# reports文件夹路径
reports_dir = os.path.join(base_dir, 'reports')
reports_html = os.path.join(reports_dir, 'reports.html')  # reports文件夹路径

# logs文件夹路径
logs_dir = os.path.join(base_dir, 'logs')
logs_file = os.path.join(logs_dir, 'logs.log')
error_file = os.path.join(logs_dir, 'error.log')

testcases_dir = os.path.join(base_dir, 'testcases')

