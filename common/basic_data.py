# -*- coding: utf-8 -*-
# @Time     : 2018/12/24/20:39
# @Author   : Hester Xu
# @Email    : 1603046502@qq.com
# @Software : PyCharm
# @File     : basic_data.py
# @Function : 测试正则以及上下文

import re

class DoRegex:
    # 查找并且替换
    # --通过正则取excel的数据，Context覆盖excel的数据
    @staticmethod
    def replace(target):  # target--excel里面要被替换的目标
        pattern = '\$\{(.*?)\}'
        while re.search(pattern, target):  # 找到一个就返回match
            m = re.search(pattern, target)
            key = m.group(1)  # invest_user
            user = getattr(Context, key)
            # print(user)  # 13537821056
            # user2 = Context.invest_user
            # print(user2)  # 13537821056
            target = re.sub(pattern, user, target, count=1)  # 替换excel中的数据
        return target   # 替换后excel中的数据


"""执行用例时，把从excel取到的数据，通过正则解析出来，再通过setattar() 放到Context的属性里，保存。
使用时通过getattr()取出来使用。"""

from common.config import CofigLoader

class Context:
    # --从配置文件取到基础数据 --放到Context的属性
    config = CofigLoader()  # 用ConfigLoader 从配置文件读取数据
    # 投资人测试数据
    invest_user = config.get('basic', 'invest_user')   # 类里面的变量是类变量  # 初始化函数里面的变量是成员变量
    invest_pwd = config.get('basic', 'invest_pwd')
    invest_member_id = config.get('basic', 'invest_member_id')
    invest_recharge_amount = config.get('basic', 'invest_recharge_amount')
    invest_withdraw_amount = config.get('basic', 'invest_withdraw_amount')
    invest_bidLoan_amount = config.get('basic', 'invest_bidLoan_amount')

    # 管理员测试数据
    admin_user = config.get('basic', 'admin_user')
    admin_pwd = config.get('basic', 'admin_pwd')

    # 借款人测试数据
    loan_member_id = config.get('basic', 'loan_member_id')
    loan_add_amount = config.get('basic', 'loan_add_amount')
    loan_add_title = config.get('basic', 'loan_add_title')

    # 获取标的所有投资记录
    invest_List_by_loan_id = config.get('basic', 'invest_List_by_loan_id')


# 创建实例后，如果类属性和实例属性一样，则实例属性会覆盖类属性

if __name__ == '__main__':
    # # python的反射 动态获取对象里面的
    # invest_user = getattr(Context,'incest_user')  # 获取变量的值
    # print(invest_user)
    # setattr(Context,'admin_user','abc')
    # admin = getattr(Context,'admin_user')
    # print(admin)
    # if hasattr(Context,'admin_user'):
    #     delattr(Context,'admin_user')
    # else:
    #     print("没有这个属性，不删除")
    s = '{"mobilephone":"${invest_user}","pwd":"${invest_pwd}"}'
    do_regex = DoRegex()
    s = do_regex.replace(s)
    print(s)


# 变量一样时，成员变量覆盖类变量
# 不需要实例可以调用

