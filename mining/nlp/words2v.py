# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/

import os,sys

from NLP import nlp

reload(sys)
sys.setdefaultencoding('utf8')
from gensim.models import word2vec
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class W2v(nlp):
    def __init__(self,fin=None):
        self.model = None
        self.file = fin

    def load(self,fmodel):
        self.model = word2vec.Word2Vec.load(fmodel)

    def process(self,size=100,window=5,min_count=5,workers=8):
        sentences = word2vec.LineSentence(self.file)
        self.model = word2vec.Word2Vec(sentences,size=size,window=window,min_count=min_count,workers=workers)

    def save(self,fout):
        try:
            self.model.save(fout)
        except IOError:
            print self.fout, "写文件取错误请检查!"
            exit(0)


if __name__ == '__main__':
    file_txt = '/Users/wangrui/百度云同步盘/中文语料库/THUCNews/last_THUCNews_w2v.txt'
    file_model_64 = '/Users/wangrui/百度云同步盘/中文语料库/THUCNews/last_THUCNews_gensim_w2v.bin'
    file_model_200 = '/Users/wangrui/百度云同步盘/中文语料库/THUCNews/last_THUCNews_gensim_w2v_200.bin'
    w = W2v(file_txt)
    logging.info('<<<<<<<<<<<<<<<<')
    w.process(size=50)
    logging.info('>>>>>>>>>>>>>>>>')
    w.save('.//last_THUCNews_gensim_w2v_64.bin')


    print '"家装" 和 "家居" 的相似度:' + str(w.model.similarity(u'家装', u'家居'))

    # 计算某个词的相关词列表
    y2 = w.model.most_similar(u'家居', topn=20)  # 20个最相关的
    for item in y2:
        print item[0], item[1]
    print "--------\n"

    # 寻找对应关系
    y3 = w.model.most_similar([u'质量', u'不错'], [u'电脑桌'], topn=3)
    for item in y3:
        print item[0], item[1]
    print "--------\n"

    # 寻找不合群的词
    y4 = w.model.doesnt_match(u"书 书籍 教材 很 沙发 电器".split())
    print u"不合群的词：", y4
    print "--------\n"