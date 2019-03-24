# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2019 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/
from mining.nlp.tokenize import Tokenize


def test_tokenize():
    t = Tokenize(".//新闻.txt")
    t.cut()
    t.save('.//新闻切词.txt')