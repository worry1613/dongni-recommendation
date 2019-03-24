# -*- coding: utf-8 -*-
# @Time    : 2018/6/19 23:39
# @Author  : houtianba(549145583@qq.com)
# @FileName: w2v.train.py
# @Software: PyCharm
# @Blog    ：http://blog.csdn.net/worryabout/

import os,sys

reload(sys)
sys.setdefaultencoding('utf8')
from gensim.models import word2vec
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
file_txt = '/Users/wangrui/百度云同步盘/中文语料库/THUCNews/last_THUCNews_w2v.txt'
file_model_64 = '/Users/wangrui/百度云同步盘/中文语料库/THUCNews/last_THUCNews_gensim_w2v.bin'
file_model_200 = '/Users/wangrui/百度云同步盘/中文语料库/THUCNews/last_THUCNews_gensim_w2v_200.bin'
# sentences = word2vec.LineSentence(file_txt)
# model = word2vec.Word2Vec(sentences,size=200,window=5,min_count=5,workers=8)
# model.save(file_model_200)
new_model = word2vec.Word2Vec.load(file_model_200)

print '"家装" 和 "家居" 的相似度:' + str(new_model.similarity(u'家装', u'沙发'))

# 计算某个词的相关词列表
y2 = new_model.most_similar(u'家居', topn=20)  # 20个最相关的
for item in y2:
    print item[0], item[1]
print "--------\n"

# 寻找对应关系
y3 = new_model.most_similar([u'质量', u'不错'], [u'电脑桌'], topn=3)
for item in y3:
    print item[0], item[1]
print "--------\n"

# 寻找不合群的词
y4 = new_model.doesnt_match(u"书 书籍 教材 很 沙发 电器".split())
print u"不合群的词：", y4
print "--------\n"