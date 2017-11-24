#!/usr/bin/python
# -*- encoding:utf-8 -*-
# 作者:王睿
# 创建时间:2015.7.3
# 邮箱:
# GitHub: https://github.com/worry1613
# CSDN:
#
# 生成切词文件 保存，提取关键词 保存
# texttokenize.py -i 语料文件名 -s 停用词文件 -o 输出结果文件 --keywords=关键词数量  --lib=[jieba.tfidf,jeiba.textrank]
#
#        -i file         单一语料库文件，文件名默认为类型名，文件内每行默认为一个输入内容
#       -o file         生成结果文件，默认为 输入文件名.tokenize.txt
#        -s file         停用词文件
#        --keywords=关键词数量        生成关键词，默认8
#       --lib=开发库     jieba.tfidf,jeiba.textrank，默认jieba.tfidf
#
#        texttokenize.py  -i s.txt  -s stopword.txt -o ~/s.tokenize.txt
#        texttokenize.py  -i ss.txt -s stopW.txt

import getopt
import traceback
import sys, os

import jieba
import jieba.analyse

reload(sys)
sys.setdefaultencoding('utf8')

import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# 语料输入文件
infile = None
# 输出语料分词文件
outfile = None
# 停用词文件
stopwordsfile = None
# 输出关键词文件
keywordfile = None
keyword = 0
minword = 0
# lib = 'jieba'
lib = ''
stopwordlist = []

cutwordmodel = jieba.analyse


def jiebakeyword(document, k=keyword):
    """
    用结巴生成关键词
    :param document:     文本内容
    :param k:            关键词个数
    :return:             关键词列表
    """
    doc = []
    i = keyword
    libs = lib.split('.')
    # for i in range(minword,keyword):
    if 'tfidf' in libs:
        doc.append(cutwordmodel.extract_tags(document, topK=i, withWeight=False, allowPOS=('ns', 'n')))
    else:
        doc.append(cutwordmodel.textrank(document, topK=i, allowPOS=('ns', 'n'), withWeight=False))
    return doc

# 分词 - 中文
def tokenize_chinese(document, keyfunc=None):
    # type: (object, object) -> object
    try:
        keys = None
        if keyfunc is not None:
            keys = keyfunc(document, keyword)
            for key in keys:
                logging.info('key=%s' % (' '.join([w for w in key])))
        word_list = [doc for doc in jieba.cut(document.strip(), cut_all=False) if doc not in stopwordlist]
        return word_list, keys
    except Exception, e:
        print traceback.print_exc()


def getfilewords(f, type='line'):
    """
    操作语料文件
    :param f:     文件名
    :param type:  操作类型，line-文件每行一个语料，file-文件全部内容是一个语料
    :return:    words
    """
    wk = []
    docs = open(f)
    if type == 'line':
        libs = lib.split('.')
        lines = docs.readlines()
        if 'jieba' in libs:
            wk = [tokenize_chinese(document=line,keyfunc=jiebakeyword) for line in lines]
        else:
            wk = [tokenize_chinese(document=line) for line in lines]
    elif type == 'file':
        wk = tokenize_chinese(document=docs.read().replace('\r\n', ''))
    docs.close()
    return wk

def genkeywordoutfile(f, keywords='tokenize'):
    """
    生成带keywords输出文件
    :param f:               输入文件
    :param keywords:        新文件名关那键词
    :return:        生成的新文件名
    输入              输出
    tt,tokenize              tt-tokenize
    tt.txt,tokenize          tt-tokenize.txt
    ./s.txt,tokenize         ./x-tokenize.txt
    tt,key                   tt-key
    tt.txt,key               tt-key.txt
    ./s.txt,key              ./x-key.txt
    """
    name = None
    paths = f.split('/')
    names = paths[-1].split('.')
    if len(names) >= 1:
        name = '%s-%s.%s' % (names[0], keywords, names[1])
    else:
        name = '%s-%s' % (names[0], keywords)
    if len(paths) == 1:
        pass
    elif len(paths) > 1:
        name = '/'.join([path for path in paths[:-1]]) + '/' + name
    return name


if __name__ == '__main__':
    usage = """
        texttokenize.py -i 语料文件名 -s 停用词文件 -o 输出结果文件 --keywords=关键词数量  --lib=[jieba.tfidf,jeiba.textrank]

        -i file         单一语料库文件，文件名默认为类型名，文件内每行默认为一个输入内容
        -o file         生成结果文件，默认为 输入文件名.tokenize.txt
        -s file         停用词文件
        --keywords=关键词数量        生成关键词，默认0
        --lib=开发库     jieba.tfidf,jeiba.textrank，默认jieba.tfidf

        texttokenize.py  -i s.txt  -s stopword.txt -o ~/s.tokenize.txt
        texttokenize.py  -i ss.txt -s stopW.txt
        """

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:s:", ["input=", "output=", "stopwords=", "keywords=", "lib="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()

    for k, v in opts:
        if k in ('-i', '--input'):
            if v != '':
                infile = v
        elif k in ('-o', '--output'):
            outfile = v
        elif k in ('-s', '--stopwords'):
            stopwordsfile = v
        elif k in '--keywords':
            keyword = v
        elif k in '--lib':
            lib = v
        elif k in ('-h', '--help'):
            print(usage)

    words = []
    keys = []
    if stopwordsfile is not None:
        stopwordlist = open(stopwordsfile).read().split('\r\n')
    if outfile is None:
        outfile = genkeywordoutfile(infile)
    keywordfile = genkeywordoutfile(infile,keywords='keyword.'+lib)
    logging.info('input=%s,\nstopwords=%s,\noutput=%s,\nkeywordfile=%s,\nkeyword=%d,lib=%s' %
                 (infile, stopwordsfile, outfile, keywordfile, keyword, lib))
    cutwordmodel.set_stop_words(stop_words_path=stopwordsfile)

    if infile is not None:
        # 单一文件语料内容
        words = getfilewords(infile)
        f = open(outfile, mode='w')
        f1 = open(keywordfile, mode='a+')
        # f1.write(' type %s \n' % (lib,))
        for wk in words:
            f.write(' '.join([ words for words in wk[0]]) + '\n')
            if wk[1] is not None:
                f1.write(' '.join([ words for words in wk[1]]) + '\n')
        f1.close()
        f.close()
    else:
        print(usage)
