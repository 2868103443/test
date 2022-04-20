#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 10 6 * * ?
new Env('易班-每日登录');
tag: yb_every_login
"""
from common import YiBan, Setting, Env


class EveryLogin:
    def __init__(self):
        self.label = 'yb_every_login'
        self.env = Env(self.label)
        self.st = Setting(self.label)

    def run(self):
        yb = YiBan()
        result = self.env.get_env('YB_COOKIE')
        if result['code'] != 1:
            self.st.msg_(-999, result['msg'])
            return 0

        for i in result['data']:
            for count in range(3):
                lit = i['remarks'].split('|')
                if len(lit) != 2:
                    self.st.msg_(-1, '账号密码分割出错 ', data={'value': i['remarks']})
                    break

                account = lit[0]
                try:
                    result = yb.mobile_auto_login(i['value'])
                    self.st.msg_(result['code'], result['msg'], data=result['data'], phone=account)
                    if result['code'] == 100:
                        break
                except Exception as ex:
                    self.st.msg_(-1, '登录异常 %s' % ex, phone=account)

        self.st.msg_(2000, f"[{self.label}]执行完成。")
        return 0
