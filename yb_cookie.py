#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 6 * * ?
new Env('易班-Cookie更新');
tag: yb_cookie
"""

from common import YiBan, Setting, Env, Excel


class Cookie:
    def __init__(self):
        self.label = 'yb_cookie'
        self.env = Env(self.label)
        self.st = Setting(self.label)

    def run(self):
        result = self.env.get_env('YB_COOKIE')
        if result['code'] != 1:
            self.st.msg_(-999, result['msg'])
            return 0

        xlsx = Excel(self.env.check_excel_file())
        if xlsx.is_already_opened_in_write():
            self.st.msg_(-999, '请先关闭Excel文件')
            return 0

        user_list = []
        for i in result['data']:
            # 遍历 'YB_COOKIE'

            yb = YiBan()

            account = i['account']
            password = i['password']
            yiban_token = i['value']
            status = 0
            for count in range(3):
                status = 0
                try:
                    result = yb.chrome_login(account, password)
                    if result['code'] == 711:
                        self.st.msg_(result['code'], '第 %d次登录失败 %s' % (count, result['message']),
                                     data={'loginCount': count}, phone=account)
                        status = 1
                        continue
                    if result['code'] != 200:
                        self.st.msg_(result['code'], '登录失败 %s' % (result['message']), phone=account)
                        status = 1
                        continue
                    yiban_token = f'yiban_user_token={result["yiban_user_token"]};'
                    self.st.msg_(result['code'], result['message'], data=result['data'], phone=account)
                    break
                except Exception as ex:
                    self.st.msg_(-1, '更新Cookie失败 ', phone=account)

            temp = {
                'name': i['name'],
                'value': yiban_token,
                'remarks': i['remarks'],
                'account': account,
                'password': password,
                'status': status
            }
            user_list.append(temp)

        # 保存Excel
        r1 = xlsx.save_data(user_list)
        self.st.msg_(r1['code'], r1['msg'])
        self.st.msg_(2000, f"[{self.label}]执行完成。")
        return 0
