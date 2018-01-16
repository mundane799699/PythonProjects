#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author  : mundane
# @date    : 2018/1/7
# @file    : Test.py
# @desc    : 递归打印1到100


def print_n(n):
    if n:
        print('%d' % n)
        print_n(n-1)
    return


if __name__ == '__main__':
    # print_n(100)
    with open('test.txt', 'w', encoding='utf-8') as f:
        f.write('### 本答案原始链接: https://www.zhihu.com/question/37400041/answer/74744187')
        f.close()

