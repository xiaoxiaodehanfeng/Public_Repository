# -*- coding: utf-8 -*-
# @Time     : 2019/1/4/20:08
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : run_test.py
# @Function : 执行用例

import unittest
import HTMLTestRunnerNew
from common import contants

# 自动查找testcases目录下，以test开头的.py文件里面的测试类
discover = unittest.defaultTestLoader.discover(contants.testcases_dir, pattern="test*.py", top_level_dir=None)

with open(contants.reports_html, 'wb') as file:
    runner = HTMLTestRunnerNew.HTMLTestRunner(stream=file, title='API测试报告')
    runner.run(discover)   # 执行查找到的用例

