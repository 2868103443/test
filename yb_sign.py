#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 7 * * ?
new Env('易班-每日签到');
tag: yb_sign
"""

import requests
from common import Setting, Env


class Sign:

    def __init__(self):
        self.label = 'yb_sign'
        self.env = Env(self.label)
        self.st = Setting(self.label)

    def set_sign(self, cookie):
        url = 'https://www.yiban.cn/ajax/checkin/answer'
        param = {
            "optionid[]": 22571,
            "input": "",
        }
        headers = {
            'Cookie': cookie,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Connection': 'keep-alive',
            'Referer': 'https://www.yiban.cn/user/info/index',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'www.yiban.cn',
            'User-Agent': self.env.UserAgent2,
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        try:
            resp = requests.post(url=url, data=param, verify=False, headers=headers, timeout=60).json()
            return {'code': int(resp['code']), 'msg': resp['message']}
        except Exception as ex:
            return {'code': -1, 'msg': '签到失败' + str(ex)}

    def run(self):
        result = self.env.get_env('YB_COOKIE')
        if result['code'] != 1:
            self.st.msg_(-999, result['msg'])
            return 0

        for i in result['data']:
            lit = i['remarks'].split('|')
            if len(lit) != 2:
                self.st.msg_(-1, '账号密码分割出错 ', data={'value': i['remarks']})
                break
            account = lit[0]

            for count in range(3):
                try:
                    result = self.set_sign(i['value'])
                    self.st.msg_(result['code'], result['msg'], phone=account)
                    if result['code'] == 200 or result['code'] == 212:
                        break
                except Exception as ex:
                    self.st.msg_(-1, ex, phone=account)

        self.st.msg_(2000, f"[{self.label}]执行完成。")
        return 0
