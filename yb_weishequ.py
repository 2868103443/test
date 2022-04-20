#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
cron: 0 0 7 * * ?
new Env('易班-微社区');
tag: yb_weishequ
"""
import json
import random
import threading
import requests
from time import sleep
from common import YiBan, OneSay, Setting, Env


class WeiSheQu:

    def __init__(self):
        self.YB_CONTENT = []
        self.one = OneSay()
        self.GET_ONE = True  # 获取一言句子
        self.love_interval = 4  # 点赞间隔
        self.comment_interval = 70  # 评论间隔
        self.advanced_interval = 70  # 发布间隔

        self.label = 'yb_weishequ'
        self.env = Env(self.label)
        self.st = Setting(self.label)

    def get_token(self, cookie):
        # 获取csrfToken
        url = 'https://s.yiban.cn/api/security/getToken'
        headers = {
            'Cookie': cookie,
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 's.yiban.cn',
            'User-Agent': self.env.UserAgent2,
        }
        try:
            resp = requests.post(url=url, headers=headers)
            ret = json.loads(resp.text)
            if ret['status']:
                data = {
                    'csrfToken': ret['data']['csrfToken'],
                    'PHPSESSID': resp.cookies.get('PHPSESSID')
                }
            else:
                data = None
            return {'code': int(ret['code']), 'msg': ret['message'], 'data': data}
        except Exception as ex:
            return {'code': -1, 'msg': '获取csrfToken失败' + str(ex)}

    def get_list_by_board(self, offset, count):
        url = "https://s.yiban.cn/api/forum/getListByBoard?"
        params = {
            'offset': offset,
            'count': count,
            'boardId': 'EqGilbKmdn62Ka3',
            'orgId': '2006794'  # 杂谈
        }
        headers = {
            'User-Agent': self.env.UserAgent2
        }
        try:
            resp = requests.get(url, params=params, headers=headers).json()
            return {'code': int(resp['code']), 'msg': resp['message'], 'data': resp['data']}
        except Exception as ex:
            return {'code': -1, 'msg': str(ex)}

    # 点赞
    def set_love(self, ls, ck):
        for n in ls:
            post_id = n['id']
            user_id = n['user']['id']
            consume = 0.0
            for i in ck:
                url = "https://s.yiban.cn/api/post/thumb"
                params = {
                    'action': 'up',
                    'postId': post_id,
                    'userId': user_id
                }
                headers = {
                    'User-Agent': self.env.UserAgent2,
                    'Cookie': i['cookie']
                }
                try:
                    resp = requests.post(url, data=json.dumps(params, indent=2), headers=headers)
                    consume += resp.elapsed.total_seconds() if resp.elapsed.total_seconds() > 0 else 0
                    resp = resp.json()
                    self.st.msg_(resp['code'], '[点赞] %s' % resp['message'], data={'type': 'love'}, phone=i['account'])
                except Exception as ex:
                    self.st.msg_(-1, '[点赞] %s' % str(ex), data={'type': 'love'}, phone=i['account'])
            s = 1 if consume > self.love_interval else round(self.love_interval - consume, 3)
            sleep(s)

    # 评论
    def set_comment(self, ls, ck, pl):
        # 评论数量
        num = len(pl) - 1
        for n in ls:
            post_id = n['id']
            user_id = n['user']['id']
            consume = 0.0
            for i in ck:
                comment = pl[random.randint(0, num)] + str(random.randint(0, 9999))
                url = 'https://s.yiban.cn/api/post/comment'
                params = {
                    'postId': post_id,
                    'comment': comment,
                    'userId': user_id,
                    'csrfToken': i['csrfToken']
                }
                headers = {
                    'User-Agent': self.env.UserAgent2,
                    'Cookie': i['cookie']
                }
                try:
                    resp = requests.post(url, data=json.dumps(params, indent=2), headers=headers)
                    consume += resp.elapsed.total_seconds() if resp.elapsed.total_seconds() > 0 else 0
                    resp = resp.json()
                    if resp['status']:
                        self.st.msg_(resp['code'], '[评论] %s' % resp['message'],
                                     data={'type': 'comment', 'comment': comment, 'commentId': resp['data']},
                                     phone=i['account'])
                        self.del_comment(resp['data'], i['cookie'], i['account'])
                    else:
                        self.st.msg_(resp['code'], '[评论] %s' % resp['message'],
                                     data={'type': 'comment', 'comment': comment},
                                     phone=i['account'])
                except Exception as ex:
                    self.st.msg_(-1, '[评论]%s' % str(ex), data={'type': 'comment'}, phone=i['account'])
            s = 0.5 if consume > self.comment_interval else round(self.comment_interval - consume, 3)
            sleep(s)

    def del_comment(self, post_id, ck, users):
        url = 'https://s.yiban.cn/api/post/delComment'
        params = {
            'commentId': post_id,
        }
        headers = {
            'User-Agent': self.env.UserAgent2,
            'Cookie': ck
        }
        try:
            resp = requests.post(url, data=json.dumps(params, indent=2), headers=headers).json()
            self.st.msg_(resp['code'], '[删除评论] %s' % resp['message'], data=params, phone=users)
        except Exception as ex:
            self.st.msg_(-1, '[删除评论] %s' % str(ex), phone=users)

    # 发帖
    def set_advanced(self, ck, count):

        while True:
            if len(self.YB_CONTENT):
                sleep(5)
                break

        # 数量
        for n in range(count):
            consume = 0.0
            for i in ck:
                num = random.randint(0, len(self.YB_CONTENT) - 1)
                content = self.YB_CONTENT[num]['content']
                title = self.YB_CONTENT[num]['title']
                url = 'https://s.yiban.cn/api/post/advanced'
                params = {
                    'channel': [
                        {
                            "boardId": "EqGilbKmdn62Ka3",
                            "orgId": 2006794
                        }
                    ],  # 杂谈
                    'content': "<p>" + content + "<p>",
                    'hasVLink': 0,
                    'isPublic': 1,  # 公开
                    'summary': '',
                    'thumbType': 1,
                    'title': title
                }
                headers = {
                    'User-Agent': self.env.UserAgent2,
                    'Cookie': i['cookie'],
                    'Host': 's.yiban.cn'
                }
                try:
                    resp = requests.post(url, data=json.dumps(params), headers=headers)
                    consume += resp.elapsed.total_seconds() if resp.elapsed.total_seconds() > 0 else 0
                    resp = resp.json()
                    self.st.msg_(resp['code'], '[发帖] %s' % resp['message'],
                                 data={'content': content, 'title': title, 'type': 'add'}, phone=i['account'])
                except Exception as ex:
                    self.st.msg_(-1, '[发帖] %s' % str(ex), data={'content': content, 'title': title, 'type': 'add'},
                                 phone=i['account'])
            s = 0.5 if consume > self.advanced_interval else round(self.advanced_interval - consume, 3)
            sleep(s)
        self.GET_ONE = False

    def get_one(self):
        while self.GET_ONE:
            ret = self.one.get_()
            if ret['code']:
                self.YB_CONTENT.append({
                    'title': ret['data']['title'],
                    'content': ret['data']['content'],
                })
            sleep(2)

    # 脚本
    def run(self):
        list_num = 35
        add_num = 20
        # 获取微社区列表
        lst = []
        for count in range(3):
            result = self.get_list_by_board(10, list_num)
            if result['code'] != 200:
                self.st.msg_(result['code'], '获取微社区列表失败 %s ' % (result['msg']))
                continue
            lst = result['data']['list']
            break

        if len(lst) == 0:
            self.st.msg_(-1, '微社区评论列表为空')

        # 获取评论发布内容
        result = self.env.get_env('YB_COMMENT')
        if result['code'] != 1:
            result = {'data': [{'value': '打卡打卡打卡打卡打卡'}]}
        yb_comment = result['data'][0]['value'].split('|')

        # result = self.env.get_env('self.YB_CONTENT')
        # if result['code'] != 1:
        #     result = {'data': ['坚持坚持再坚持，努力努力再努力！']}
        # self.YB_CONTENT = result['data'][0].split('|')

        # 获取用户Cookie
        result = self.env.get_env('YB_COOKIE')
        if result['code'] != 1:
            self.st.msg_(-999, result['msg'])
            return 0

        cookies = []
        # 检查 token, 获取评论 token
        for i in result['data']:
            lit = i['remarks'].split('|')
            if len(lit) != 2:
                self.st.msg_(-1, '账号密码分割出错 ', data={'value': i['remarks']})
                break
            account = lit[0]

            for count in range(3):
                try:

                    check = YiBan.check_token(i['value'])
                    if check['code'] != 200:
                        self.st.msg_(check['code'], 'token失效 %s' % (check['msg']), phone=account)
                        continue
                    # 获取评论 csrfToken
                    result = self.get_token(i['value'])
                    if result['code'] != 200:
                        self.st.msg_(result['code'], '[csrfToken] %s' % result['msg'], phone=account)
                        continue
                    temp = {
                        'userId': check['data']['userId'],
                        'csrfToken': result['data']['csrfToken'],
                        'cookie': i['value'] + '; PHPSESSID=' + result['data']['PHPSESSID'],
                        'account': account
                    }
                    cookies.append(temp)
                    break
                except Exception as ex:
                    self.st.msg_(-1, '微社区 %s' % ex)

        if len(cookies) < 1:
            self.st.msg_(-999, '可用cookie为空。')
            return 0

        try:
            # 点赞
            _love = threading.Thread(target=self.set_love, args=(lst, cookies,))
            # 评论
            _comment = threading.Thread(target=self.set_comment, args=(lst, cookies, yb_comment,))
            # 发帖
            _advanced = threading.Thread(target=self.set_advanced, args=(cookies, add_num,))
            # 一言
            _one = threading.Thread(target=self.get_one)

            _love.start()
            _comment.start()
            _one.start()
            _advanced.start()

            _love.join()
            _comment.join()
            _advanced.join()
        except Exception as ex:
            self.st.msg_(-1, '微社区 %s' % ex)

        self.st.msg_(2000, f"[{self.label}]执行完成。")
        return 0
