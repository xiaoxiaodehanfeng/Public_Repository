# -*- coding: utf-8 -*-
# @Time     : 2018/12/17/16:06
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @File     : config.py
# @Software : PyCharm

# 配置文件的读取

import configparser
import os
from common import contants

class CofigLoader:

    def __init__(self):
        self.conf = configparser.ConfigParser()  # 创建实例
        # 加载配置文件 global.conf
        file_name = os.path.join(contants.configs_dir, 'global.conf')
        self.conf.read(filenames=file_name,encoding='utf-8')  # 加载配置文件
        if self.getboolean('switch','on'):  # 环境切换总开关，on=True：加载online.conf
            online_file_name = os.path.join(contants.configs_dir, 'online.conf')
            self.conf.read(filenames=online_file_name, encoding='utf-8')  # 加载配置文件 online.conf
        else:  # on=False：加载 test.conf
            test_file_name = os.path.join(contants.configs_dir, 'test.conf')
            self.conf.read(filenames=test_file_name, encoding='utf-8')  # 加载配置文件 test.conf

    def get(self,section,option): # 根据section，option 来取到配置的值
        return self.conf.get(section,option) # 返回str类型的值

    def getint(self, section, option):  # 根据section，option 来取到配置的值
        return self.conf.getint(section, option)  # 返回str类型的值

    def getfloat(self, section, option):  # 根据section，option 来取到配置的值
        return self.conf.getfloat(section, option)  # 返回float类型的值

    def getboolean(self, section, option):  # 根据section，option 来取到配置的值
        return self.conf.getboolean(section, option)  # 返回str类型的值

if __name__ == '__main__':
    config = CofigLoader()  # 创建实例
    # url_pre = config.get('api','url_pre')
    # print(type(url_pre),url_pre)
    invest_user = config.get('basic','invest_user')
    print(invest_user)

