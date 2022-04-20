#!/usr/bin/env python3
# -*- coding: utf-8 -*
import os
from yb_cookie import Cookie
from yb_every_login import EveryLogin
from yb_sign import Sign
from yb_miaomiao import MiaoMiao
from yb_weishequ import WeiSheQu
from yb_total_salary import TotalSalary
from yb_yiban_pay import YibanPay
from yb_yiban_sign import YibanSign

def main():
        # 全部
    EveryLogin().run()
    Sign().run()
    MiaoMiao().run()
    WeiSheQu().run()
    TotalSalary().run()
