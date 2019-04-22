# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

import sys, os
from optparse import OptionParser

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

    def __init__(self, fin, userdict=None, stopdict=stopd):
        """

        :param fin: 语料库文件
        :param userdict: 自定义词典
        :param stopdict: 停用词典
        """
        self.fin = fin
        self.stopd = stopdict
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

        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        jieba.enable_parallel(cpu_count)
        lines = docs.readlines()
        logging.info('%d lines ======%d workers' % (len(lines),cpu_count))
        self.result = [[doc.strip() for doc in jieba.cut(line.strip(), cut_all=False) if doc not in stopwords] for line
                       in lines]
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
    parser = OptionParser()
    parser.add_option('-i', '--in', type=str, help='语料库文件', dest='corpusfile')
    parser.add_option('-o', '--out', type=str, help='分完词的文件', dest='wordsfile')
    parser.add_option('-w', '--word', type=str, help='自定义词典文件', dest='wordsdict')
    parser.add_option('-s', '--stop', type=str, help='停用词词典文件', dest='stopwords')

    options, args = parser.parse_args()
    if not (options.corpusfile or options.wordsfile):
        parser.print_help()
        exit()

    t = Fenci(options.corpusfile, options.wordsdict)
    t.cut(options.wordsfile)
