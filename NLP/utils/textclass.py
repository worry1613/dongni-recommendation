#!/usr/bin/python
# -*- encoding:utf-8 -*-
# 作者:王睿
# 创建时间:2015.7.3
# 邮箱:
# GitHub: https://github.com/worry1613
# CSDN:   https://blog.csdn.net/worryabout/

import getopt
import traceback
import jieba
import sys,os

from gensim import corpora
from gensim import models

reload(sys)
sys.setdefaultencoding('utf8')

import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

infile = 0
indir = 0
outdir = './'
stopwords = 0
classtype = 'TFIDF'
txtType = ''
txtTypes = []
stopwordlist = []

dictionary = None
corpus = None
model = None



def addstopwords(f):
    """
    加停用词表
    :param f:   停用词文件
    :return:
    """
    try:
        stopwordlist = open(f).read().split('\r\n')
    except Exception,e:
        raise e.message
    return stopwordlist

def etl(w,stopwords):
    """
    去掉停用词
    :param w:           词
    :param stopwords:   停用词列表
    :return:
    """
    if w not in stopwords:
        return w
    else:
        return ''

def tokenize_chinese(document,onlychn,stopwords):
    """
    分词
    :param document:
    :param onlychn:
    :param stopwords:
    :return:
    """
    try:
        word_list = filter(lambda x: len(x) > 0, map(etl, jieba.cut(document.strip(), cut_all=False)))
        return word_list
    except Exception, e:
        print traceback.print_exc()


# 训练tf_idf模型
def tf_idf_trainning(documents_token_list):
    try:
        # 将所有文章的token_list映射为 vsm空间
        dictionary = corpora.Dictionary(documents_token_list)
        # 每篇document在vsm上的tf表示
        corpus_tf = [ dictionary.doc2bow(token_list) for token_list in documents_token_list ]
        # 用corpus_tf作为特征，训练tf_idf_model
        tf_idf_model = models.TfidfModel(corpus_tf)
        # 每篇document在vsm上的tf-idf表示
        corpus_tfidf = tf_idf_model[corpus_tf]
        #print "[INFO]: tf_idf_trainning is finished!"
        return dictionary, corpus_tf, corpus_tfidf
    except Exception,e:
        print traceback.print_exc()



def getType(file):
    """
    返回类型名
    :param file:    文件路径
    :return:        主文件名
    ./www/中文.txt   中文
    中文.txt         中文
    中文文件名        中文文件名
    ./ww/中文文件名   中文文件名

    """
    ps = file.strip('').split('/')
    fs = []
    if len(ps) == 1:
        fs = file.strip('').split('.')
    elif len(ps) > 1:
        fs = ps[-1].split('.')
    if len(fs) >= 1:
        return fs[0].strip()

def getTypeDir(dir,txtType):
    """
    返回类型名
    :param file:      目录
    :return:          主目录名
    ./www/中文/       中文
    中文/             中文
    ../ww/中文名/     中文文件名

    """
    words=[]
    txtType = txtType
    ps = dir.strip('').split('/')
    dirs = os.listdir(dir)
    for file in dirs:
        if os.path.isdir(file):
            curdir = '%s/%s'%(dir,file)
            curtype = '%s/%s'%(txtType,file)
            words = getTypeDir(curdir,curtype)
            return curtype,words
        else:
            words.append(getfilewords('%s/%s'%(dir,file),type='file')[1])

    dictionary = corpora.Dictionary(words)
    dictionary.save('%s/%s.dic' % (outdir, txtType))
    corpus = [dictionary.doc2bow(doc) for doc in words]


    return ps[-1].strip()
#
# def getType_test():
#     s = ['./www/中文.txt    ', '中文.txt    ', '  中文文件名 ', '   ./ww/中文文件名  ', './ww/中文文件名/tttt']
#     t = [getType(ss) for ss in s]
#     print t

def getfilewords(f,type='line'):
    """
    操作语料文件
    :param f:     文件名
    :param type:  操作类型，line-文件每行一个语料，file-文件全部内容是一个语料
    :return:    type, words
    """
    txtType = getType(f)
    words = []
    docs = open(f)
    if type == 'line':
        lines = docs.readlines()
        words = [tokenize_chinese(document=line) for line in lines]
    elif type == 'file':
        words = tokenize_chinese(document=docs.read().replace('\r\n',''))
    docs.close()
    return txtType,words

def getdirwords(d):
    """
    操作语料目录
    :param f:     目录名
    :return:    type, words
    """
    txtType = None
    words = None
    txtType,words = getTypeDir(d)
    # words = []
    # docs = open(f)
    # if type == 'line':
    #     lines = docs.readlines()
    #     words = [tokenize_chinese(document=line) for line in lines]
    # elif type == 'file':
    #     words = tokenize_chinese(document=docs.read().replace('\r\n',''))
    # docs.close()
    return txtType,words

if __name__ == '__main__':
    usage = """
        主要用来作文本分类
        textclass.py -i 语料文件名 -s 停词字典文件 -t 分类模型 -o 输出结果目录

        -f file         单一语料库文件，文件名默认为类型名，文件内每行默认为一个输入内容
        -d dir          语料库文件目录，目录内的每个文件默认为一个输入内容
        -o dir          输出目录，默认为当前目录
        -s file         停用词字典文件
        -t type         TFIDF,LDA,LSA,LSI,NB,SVM,FASTTEXT
        -n classname    分类名

        textclass.py  -f ss.txt -o ~/ -t lda
        textclass.py -d /stop/  -o ~/stopword/ -t lsa
        """

    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:d:o:s:t:n:", ["file=", "indir=", "outdir=", "stop=", "type=", "name="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()

    for k, v in opts:
        if k in ('-f', '--file'):
            if v != '':
                infile = v
        elif k in ('-d', '--indir'):
            indir = v
        elif k in ('-o', '--outdir'):
            outdir = v
        elif k in ('-s', '--stop'):
            stopwords = v
        elif k in ('-h', '--help'):
            print(usage)
        elif k in ('-t', '--type'):
            print(usage)
    print('infile=%s,indir=%s,outdir=%s,stopwords=%s,type=%s' % (infile, indir, outdir, stopwords, type))

    words = []
    if stopwords != 0:
        stopwordlist = open(stopwords).read().split('\r\n')
    if infile is not 0:
        # 单一文件语料内容
        txtType,words = getfilewords(infile)
        dictionary = corpora.Dictionary(words)
        dictionary.save('%s/%s.dic' % (outdir,txtType))
        corpus = [dictionary.doc2bow(doc) for doc in words]
        models.TfidfModel


        # print(words)
    elif indir is not 0:
        txtType, words = getdirword(indir)
    else:
        print(usage)
