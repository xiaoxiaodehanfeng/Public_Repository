# -*- coding: utf-8 -*-
# @Time     : 2018/12/14/10:50
# @Author   : Hester Xu
# Email     : 1603046502@qq.com
# @File     : request.py
# @Software : PyCharm

# 写一个http请求的类
import requests
import json
from common.config import CofigLoader

"""Requests封装类
实现只需调用一个方法，来支持完成多种请求方式（get,post,delete....）的请求"""

class Request:
    def __init__(self, method, url, data=None, cookies=None, headers=None):
        try:          # 异常处理
            config = CofigLoader()
            url_pre = config.get('api', 'url_pre')
            url = url_pre + url  # 拼接请求地址
            if method == 'get':
                self.resp = requests.get(url=url,params=data,cookies=cookies,headers=headers)
            elif method == 'post':
                self.resp = requests.post(url=url, data=data, cookies=cookies, headers=headers)
            elif method == 'put':
                self.resp = requests.put(url=url, data=data, cookies=cookies, headers=headers)
            elif method == 'head':
                self.resp = requests.head(url=url, data=data, cookies=cookies, headers=headers)
            elif method == 'delete':
                self.resp = requests.delete(url=url, data=data, cookies=cookies, headers=headers)
            elif method == 'options':
                self.resp = requests.options(url=url, data=data, cookies=cookies, headers=headers)
            elif method == 'patch':
                self.resp = requests.patch(url=url, data=data, cookies=cookies, headers=headers)

        except Exception as e:  # 异常从小到大
            raise e

    def get_status_code(self):   # 返回响应码
        return self.resp.status_code

    def get_text(self):   # 返回str类型的响应体
        return self.resp.text

    def get_json(self):   # 返回dict类型的响应体
        json_dict = self.resp.json()
        # 通过json.dumps函数将字典转换成格式化后的字符串
        resp_text = json.dumps(json_dict, ensure_ascii=False, indent=4)
        # print("response：", resp_text)
        return json_dict

    def get_cookies(self, key=None):  # 返回cookies
        print(self.resp.cookies)
        if key is not None:
            return self.resp.cookies[key]
        else:  # key=None，返回整个cookies对象
            return self.resp.cookies

    # 怎么取cookies里的JSESSIONID

