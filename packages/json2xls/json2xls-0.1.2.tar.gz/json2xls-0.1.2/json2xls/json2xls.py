#!/usr/bin/env python
#-*- coding:utf-8 -*-
import json
import requests
import os
import click
import xlwt
import collections
from xlwt import Workbook
from functools import partial
from collections import OrderedDict

json_dumps = partial(json.dumps, ensure_ascii=False)
json_loads = partial(json.loads, object_pairs_hook=OrderedDict)


class Json2Xls(object):
    """Json2Xls API 接口

    :param string filename: 指定需要生成的的excel的文件名

    :param string url_or_json: 指定json数据来源，
       可以是一个返回json的url，
       也可以是一行json字符串，
       也可以是一个包含每行一个json的文本文件

    :param string method: 当数据来源为url时，请求url的方法，
       默认为get请求

    :param dict params: get请求参数，默认为 :py:class:`None`

    :param dict data: post请求参数，默认为 :py:class:`None`

    :param dict headers: 请求url时的HTTP头信息

    :param bool form_encoded: post请求时是否作为表单请求，默认为 :py:class:`False`

    :param string sheet_name: Excel的sheet名称，默认为 sheet0

    :param string title_style: Excel的表头样式，默认为 :py:class:`None`
    """

    def __init__(self, filename, url_or_json, method='get',
                 params=None, data=None, headers=None, form_encoded=False,
                 sheet_name='sheet0', title_style=None):
        self.sheet_name = sheet_name
        self.filename = filename
        self.url_or_json = url_or_json
        self.method = method
        self.params = params
        self.data = data
        self.headers = headers
        self.form_encoded = form_encoded

        self.__check_file_suffix()

        self.book = Workbook(encoding='utf-8', style_compression=2)
        self.sheet = self.book.add_sheet(self.sheet_name)

        self.start_row = 0

        self.title_style = xlwt.easyxf(title_style or
                                       'font: name Arial, bold on;'
                                       'align: vert centre, horiz center;'
                                       'borders: top 1, bottom 1, left 1, right 1;'
                                       'pattern: pattern solid, fore_colour lime;'
                                       )

    def __check_file_suffix(self):
        suffix = self.filename.split('.')[-1]
        if '.' not in self.filename:
            self.filename += '.xls'
        elif suffix != 'xls':
            raise Exception('filename suffix must be .xls')

    def __get_json(self):
        data = None
        try:
            data = json_loads(self.url_or_json)
        except:
            if os.path.isfile(self.url_or_json):
                with open(self.url_or_json, 'r') as source:
                    data = [json_loads(line.decode('utf-8')) for line in source]
            else:
                try:
                    if self.method.lower() == 'get':
                        resp = requests.get(self.url_or_json,
                                            params=self.params,
                                            headers=self.headers)
                        data = resp.json()
                    else:
                        if os.path.isfile(self.data):
                            with open(self.data, 'r') as source:
                                self.data = [json_loads(line.decode('utf-8')) for line in source]
                        if not self.form_encoded:
                            self.data = json.dumps(self.data)
                        resp = requests.post(self.url_or_json,
                                             data=self.data, headers=self.headers)
                        data = resp.json()
                except Exception as e:
                    print e
        return data

    def __fill_title(self, data):
        '''生成默认title'''
        data = self.flatten(data)
        for index, key in enumerate(data.keys()):
            key = json_dumps(key)
            try:
                self.sheet.col(index).width = (len(key) + 1) * 256
            except:
                pass
            self.sheet.row(self.start_row).write(index,
                                                       key, self.title_style)
        self.start_row += 1

    def __fill_data(self, data):
        '''生成默认sheet'''
        data = self.flatten(data)
        for index, value in enumerate(data.values()):
            value = json_dumps(value)
            try:
                width = self.sheet.col(index).width
                new_width = min((len(value) + 1) * 256, 256 * 50)
                self.sheet.col(index).width = width if width > new_width else new_width
            except:
                pass
            self.sheet.row(self.start_row).write(index, value)

        self.start_row += 1

    def auto_width(self, row, col, value):
        '''单元格宽度自动伸缩

        :param int row: 单元格所在行下标

        :param int col: 单元格所在列下标

        :param int value: 单元格中的内容
        '''

        try:
            self.sheet.row(row).height_mismatch = True
            self.sheet.row(row).height = 0
            width = self.sheet.col(col).width
            new_width = min((len(value) + 1) * 256, 256 * 50)
            self.sheet.col(col).width = width if width > new_width else new_width
        except:
            pass

    def flatten(self, data_dict, parent_key='', sep='.'):
        '''对套嵌的dict进行flatten处理为单层dict

        :param dict data_dict: 需要处理的dict数据。

        :param str parent_key: 上层字典的key，默认为空字符串。

        :param str sep: 套嵌key flatten后的分割符， 默认为“.” 。
        '''
        items = []
        for k, v in data_dict.items():
            new_key = parent_key + sep + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(self.flatten(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return OrderedDict(items)

    def make(self, title_callback=None, body_callback=None):
        '''生成Excel。

        :param func title_callback: 自定义生成Execl表头的回调函数。
           默认为 :py:class:`None`，即采用默认方法生成

        :param func body_callback: 自定义生成Execl内容的回调函数。
           默认为 :py:class:`None`，即采用默认方法生成
        '''

        data = self.__get_json()
        print data
        if not isinstance(data, (dict, list)):
            raise Exception('bad json format')
        if isinstance(data, dict):
            data = [data]

        if title_callback != None:
            title_callback(self, data[0])
        else:
            self.__fill_title(data[0])

        if body_callback != None:
            for d in data:
                body_callback(self, d)
        else:
            for d in data:
                self.__fill_data(d)

        self.book.save(self.filename)


@click.command()
@click.argument('filename')
@click.argument('source')
@click.option('--method', '-m', default='get')
@click.option('--params', '-p', default=None)
@click.option('--data', '-d', default=None)
@click.option('--headers', '-h', default=None)
@click.option('--sheet', '-s', default='sheet0')
@click.option('--style', '-S', default=None)
@click.option('--form_encoded', '-f', is_flag=True)
def make(filename, source, method, params, data, headers, sheet, style, form_encoded):
    if isinstance(headers, basestring):
        headers = eval(headers)
    Json2Xls(filename, source, method=method, params=params,
             data=data, headers=headers, form_encoded=form_encoded, sheet_name=sheet,
             title_style=style).make()

if __name__ == '__main__':
    make()
