#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author  : mundane
# @date    : 2018/1/7
# @file    : spider.py

from Zhihu import Zhihu
from multiprocessing import Pool

if __name__ == '__main__':
    # todo 这里的header可能需要加cookie了, 因为有的作者名不加cookie拿不到真名, 只能得到一个叫做"知乎用户"的作者名,
    # 真实的作者名给隐藏了
    zhiHu = Zhihu()
    # 男生 25 岁了，应该明白哪些道理?
    # url = 'https://www.zhihu.com/question/37400041'
    question_id = '37400041'
    url_format = 'https://www.zhihu.com/api/v4/questions/{}/answers?include=data[*].content,voteup_count,created_time&offset=0&limit=20&sort_by=default'
    # https://www.zhihu.com/api/v4/questions/37400041/answers?include=data[*].content,voteup_count,created_time&offset=0&limit=20&sort_by=default
    url = url_format.format(question_id)
    zhiHu.request(url)

