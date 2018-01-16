#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author  : mundane
# @date    : 2018/1/7
# @file    : Zhihu.py
import os
import re

import html2text
import requests
import json
from requests import RequestException
from bs4 import BeautifulSoup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
}


def html_template(data):
    # api content
    html = '''
            <html>
            <head>
            <body>
            %s
            </body>
            </head>
            </html>
            ''' % data
    return html


class Zhihu(object):
    def __init__(self):
        pass

    def request(self, url):
        try:
            response = requests.get(url=url, headers=headers)
            if response.status_code == 200:
                # 不管是不是最后一条数据, 先进行解析再说
                text = response.text
                # 此处进行进一步解析
                # print('url =', url, 'text =', text)
                content = json.loads(text)
                self.parse_content(content)
                # 如果不是最后一条数据, 继续递归请求并解析
                if not content.get('paging').get('is_end'):
                    next_page_url = content.get('paging').get('next').replace('http', 'https')
                    self.request(next_page_url)

            return None
        except RequestException:
            print('请求网址错误')
            return None

    def parse_content(self, content):
        if 'data' in content.keys():
            for data in content.get('data'):
                parsed_data = self.parse_data(data)
                self.transform_to_markdown(parsed_data)

    def parse_data(self, content):
        data = {}
        answer_content = content.get('content')
        # print('content =', content)

        author_name = content.get('author').get('name')
        print('author_name =', author_name)
        answer_id = content.get('id')
        question_id = content.get('question').get('id')
        question_title = content.get('question').get('title')
        vote_up_count = content.get('voteup_count')
        create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(content.get('created_time')))

        content = html_template(answer_content)
        soup = BeautifulSoup(content, 'lxml')
        answer = soup.find("body")

        soup.body.extract()
        soup.head.insert_after(soup.new_tag("body", **{'class': 'zhi'}))

        soup.body.append(answer)

        img_list = soup.find_all("img", class_="content_image lazy")
        for img in img_list:
            img["src"] = img["data-actualsrc"]
        img_list = soup.find_all("img", class_="origin_image zh-lightbox-thumb lazy")
        for img in img_list:
            img["src"] = img["data-actualsrc"]
        noscript_list = soup.find_all("noscript")
        for noscript in noscript_list:
            noscript.extract()

        data['content'] = soup
        data['author_name'] = author_name
        data['answer_id'] = answer_id
        data['question_id'] = question_id
        data['question_title'] = question_title
        data['vote_up_count'] = vote_up_count
        data['create_time'] = create_time
        return data

    def transform_to_markdown(self, data):
        content = data['content']
        author_name = data['author_name']
        answer_id = data['answer_id']
        question_id = data['question_id']
        question_title = data['question_title']

        vote_up_count = data['vote_up_count']
        create_time = data['create_time']

        file_name = 'vote[%d]_%s的回答.md' % (vote_up_count, author_name)

        folder_name = question_title

        # 如果文件夹不存在, 就创建文件夹
        question_dir = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(question_dir):
            os.mkdir(folder_name)

        answer_path = os.path.join(os.getcwd(), folder_name, file_name)
        with open(answer_path, 'w+', encoding='utf-8') as f:
            # f.write("-" * 40 + "\n")
            origin_url = 'https://www.zhihu.com/question/{}/answer/{}'.format(question_id, answer_id)
            # print('origin_url =', origin_url)
            f.write("### 本答案原始链接: " + origin_url + "\n")
            f.write("### question_title: " + question_title + "\n")
            f.write("### Author_Name: " + author_name + "\n")
            f.write("### Answer_ID: %d" % answer_id + "\n")
            f.write("### Question_ID %d: " % question_id + "\n")
            f.write("### VoteCount: %s" % vote_up_count + "\n")
            f.write("### Create_Time: " + create_time + "\n")
            f.write("-" * 40 + "\n")

            text = html2text.html2text(content.decode('utf-8'))
            # 标题
            r = re.findall(r'\*\*(.*?)\*\*', text, re.S)
            for i in r:
                if i != " ":
                    text = text.replace(i, i.strip())

            r = re.findall(r'_(.*)_', text)
            for i in r:
                if i != " ":
                    text = text.replace(i, i.strip())
            text = text.replace('_ _', '')
            text = text.replace('_b.', '_r.')
            # 图片
            r = re.findall(r'!\[\]\((?:.*?)\)', text)
            for i in r:
                text = text.replace(i, i + "\n\n")
                folder_name = '%s/image' % os.getcwd()
                if not os.path.exists(folder_name):
                    os.mkdir(folder_name)
                img_url = re.findall('\((.*)\)', i)[0]
                save_name = img_url.split('/')[-1]
                file_path = '%s/%s' % (folder_name, save_name)

                try:
                    content = self.download_image(img_url)
                    if content:
                        self.save_image(content, file_path)
                except Exception as e:
                    print(e)
                else:  # if no exception,get here
                    text = text.replace(img_url, file_path)

            f.write(text)
            f.close()

    def download_image(self, url):
        print('正在下载图片', url)
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
        except RequestException:
            print('请求图片错误', url)
            pass

    def save_image(self, content, file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()

