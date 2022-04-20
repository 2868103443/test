#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 12 * * ?
new Env('易班-网薪统计');
tag: yb_total_salary
"""
import time
from common import YiBan, Now, Setting, Env


class TotalSalary:

    def __init__(self):
        self.yb = YiBan()
        self.label = 'yb_total_salary'
        self.env = Env(self.label)
        self.st = Setting(self.label)

    # 网薪统计 ck = cookie, t = 统计时间, page = 前 page * 100 条数据 由于没有查询 不建议查询超过3天前的数据
    def total_salary(self, ck, t=time.time(), page=5):
        # 时间格式化
        d = Now.to_date(t, '%Y-%m-%d 00:00:00')
        # 再转时间戳
        start_time = Now.to_time(d)

        d = Now.to_date(t, '%Y-%m-%d 23:59:59')
        stop_time = Now.to_time(d)

        score = 0
        p = 1
        temp = []
        while p <= page:

            result = self.yb.get_salary(ck, p)
            if result['code'] != 100:
                return {'code': 1, 'msg': '第 ' + str(p) + '页获取失败', 'data': temp, 'amount': score,
                        'date': Now.to_date(t, '%Y-%m-%d'), }

            lens = len(result['data'])
            for n in result['data']:
                create_time = Now.to_time(n['createTime'])
                if stop_time > create_time > start_time:
                    score += n['amount'] if n['amount'] > 0 else 0
                    temp.append(n)
                if start_time > create_time:
                    p = page
                    break
                if start_time < create_time and page == p:
                    page += 1
            if lens < 30:
                p = page + 1
            else:
                p += 1
        date = Now.to_date(t, '%Y-%m-%d')
        return {'code': 1, 'msg': f'操作成功 [日期: {date}, 增加: {score}网薪]', 'data': temp, 'amount': score, 'date': date}

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
            try:
                result = self.total_salary(i['value'])
                self.st.msg_(
                    result['code'], result['msg'], data={'date': result['date'], 'amount': result['amount']},
                    phone=account)
            except Exception as ex:
                self.st.msg_(-1, '%s' % ex, phone=account)
        self.st.msg_(2000, f"[{self.label}]执行完成。")
        return 0
