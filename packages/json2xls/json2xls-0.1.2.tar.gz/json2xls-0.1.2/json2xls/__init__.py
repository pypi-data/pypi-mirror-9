#!/usr/bin/env python
# coding:utf-8

"""
json2xls
===========

根据json数据生成excel表格，默认支持单层json生成Excel，多层json可以自定义生成方法。

json数据来源可以是一个返回json的url，也可以是一行json字符串，也可以是一个包含每行一个json的文本文件

安装
----

:py:mod:`json2xls` 代码托管在 `GitHub`_，并且已经发布到 `PyPI`_，可以直接通过 `pip` 安装::

    $ pip install json2xls

源码安装::

    $ python setup.py install

:py:mod:`json2xls` 以 MIT 协议发布。

.. _GitHub: https://github.com/axiaoxin/json2xls
.. _PyPI: https://pypi.python.org/pypi/json2xls

使用教程
--------

API调用::

    >>> from json2xls import Json2Xls
    >>> json_data = '{"name": "ashin", "age": 16, "sex": "male"}'
    >>> Json2Xls('test.xls', json_data).make()
    >>>
    >>> url = 'http://api.bosonnlp.com/sentiment/analysis'
    >>> Json2Xls('test.xlsx', url, method='post').make()

命令行::

    $ json2xls test.xls '{"a":"a", "b":"b"}'
    $ json2xls test.xls '[{"a":"a", "b":"b"},{"a":1, "b":2}]'
    $ json2xls test.xls "`cat tests/data.json`"
    $ json2xls test.xls tests/data2.json
    $ json2xls test.xls http://api.bosonnlp.com/ner/analysis -m post -d '"我是臭流氓"' -h "{'X-Token': 'bosontokenheader'}"

"""

__author__ = 'Axiaoxin'
__email__ = '254606826@qq.com'
__version__ = '0.1.2'

from json2xls import Json2Xls
