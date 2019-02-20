# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

import sys, os

reload(sys)
sys.setdefaultencoding('utf8')

from NLP import nlp
import jieba
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
stopd = './/stop.dict'

class Fenci(nlp):
    """
    切词类，把语料库的文本内容切词
    """
    def __init__(self, fin, userdict=None, stopdict=None):
        """

        :param fin: 语料库文件
        :param userdict: 自定义词典
        :param stopdict: 停用词典
        """
        self.fin = fin
        self.stopd = stopd if stopdict is None else stopdict
        self.result = []

        if userdict is not None:
            jieba.load_userdict(userdict)

    def cut(self, fout=None):
        """

        :param fout:
        :return:
        """
        stopwords = {}
        try:
            fstop = open(self.stopd)
        except IOError:
            print self.stopd, "文件读取错误请检查!"
            exit(0)
        for eachWord in fstop:
            stopwords[eachWord.strip().decode('utf-8', 'ignore')] = eachWord.strip().decode('utf-8', 'ignore')
        fstop.close()

        try:
            docs = open(self.fin)
        except IOError:
            print self.fin, "文件读取错误请检查!"
            exit(0)

        jieba.enable_parallel(4)
        lines = docs.readlines()
        logging.info('%d lines ======' % (len(lines),))
        for line in lines:
            self.result.append([doc.strip() for doc in jieba.cut(line.strip(), cut_all=False) if doc not in stopwords])
        docs.close()
        logging.info('>>>>>>>>>>>>>')
        if fout:
            self.save(fout=fout)

    def save(self, fout):
        """
        切好词的结果保存文件
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
    fin = ".//新闻.txt"
    fout = ".//新闻切词.txt"
    t = Fenci(fin)
    t.cut(fout)
    # t.save(fout)
