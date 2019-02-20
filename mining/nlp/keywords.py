# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

import sys, os

reload(sys)
sys.setdefaultencoding('utf8')
import jieba
import jieba.analyse
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from NLP import nlp
stopd = './/stop.dict'

class Keywords(nlp):
    """
    提取关键词类，提取语料库的文本关键词
    用textrank算法提取
    """
    def __init__(self, fin, userdict=None, stopdict=None):
        """
        :param fin: 语料库文件
        :param userdict: 自定义词典
        :param stopdict: 停用词典
        """
        self.fin = fin
        self.result = []

        if userdict is not None:
            jieba.load_userdict(userdict)
        if stopdict is not None:
            jieba.analyse.set_stop_words(stopdict)

    def gen(self, fout=None):
        """
        生成关键词
        :param fout:
        :return:
        """
        try:
            docs = open(self.fin)
        except IOError:
            print self.fin, "文件读取错误请检查!"
            exit(0)

        lines = docs.readlines()
        logging.info('%d lines ======' % (len(lines),))
        for line in lines:
            self.result.append(jieba.analyse.textrank(line, topK=3, allowPOS=('ns', 'n'), withWeight=False))
        docs.close()
        logging.info('>>>>>>>>>>>>>')
        if fout:
            self.save(fout=fout)

    def save(self, fout):
        """
        生成的关键词的结果保存文件
        :param fout:
        :return:
        """
        try:
            f = open(fout, "w")
            for words in self.result:
                f.write(" ".join(words) + "\n")
            f.close()
        except IOError:
            print self.fout, "写文件取错误请检查!"
            exit(0)


if __name__ == '__main__':
    fin = ".//新闻min.txt"
    fout = ".//新闻关键词.txt"
    t = Keywords(fin)
    t.gen(fout)
    # t.save(fout)
