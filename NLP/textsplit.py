# -*- encoding:utf-8 -*-
# 作者:王睿
# 创建时间:2015.7.3
# 邮箱:
# GitHub: https://github.com/worry1613
# CSDN:
#
# 切分训练和测试数据集
# textsplit.py -i 语料文件名 -s 停用词文件 -n 切分比例
#
#        -i file         单一语料库文件，文件名默认为类型名，文件内每行默认为一个输入内容
#        -s file         停用词文件
#        -n split        切分比例，多个用逗号分开,
#
#        textsplit.py  -i s.txt  -s stopword.txt -n 15
#        textsplit.py  -i ss.txt -s stopW.txt -n 15,25,30
import copy
import getopt
import random
import traceback
import sys, os
import jieba
import logging
reload(sys)
sys.setdefaultencoding('utf8')
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# 语料输入文件
infile = None
# 输出语料分词文件
outfile = None
# 停用词文件
stopwordsfile = None
stopwordlist = []
txtType = None
label = "__label__"
nc = 0

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

# 分词 - 中文
def tokenize_chinese(document, n):
    # type: (object, object) -> object
    try:
        word_list = [doc for doc in jieba.cut(document.strip(), cut_all=False) if doc not in stopwordlist]
        # nc+=1
        logging.info('line %d is OK' % (n,))
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
        lines = docs.readlines()
        logging.info('%d lines ======'% (len(lines),))
        wk = [tokenize_chinese(document=line,n=k) for k,line in enumerate(lines)]
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
        textsplit.py -i 语料文件名 -s 停用词文件 -n 切分比例

        -i file         单一语料库文件，文件名默认为类型名，文件内每行默认为一个输入内容
        -s file         停用词文件
        -n split        切分比例，多个用逗号分开
        -l label        分割标志符
        
        textsplit.py  -i s.txt  -s stopword.txt -n 15
        textsplit.py  -i ss.txt -s stopW.txt -n 15,25,30
        """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:n:s:l:", ["input=", "split=", "stopwords=", "label="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()
    split = None
    for k, v in opts:
        if k in ('-i', '--input'):
            if v != '':
                infile = v
        elif k in ('-n', '--split'):
            split = v.split(',')
        elif k in ('-l', '--label'):
            label = v.strip()
        elif k in ('-s', '--stopwords'):
            stopwordsfile = v
        elif k in ('-h', '--help'):
            print(usage)
    txtType = getType(infile)
    words = []
    keys = []
    if stopwordsfile is not None:
        stopwordlist = open(stopwordsfile).read().split('\r\n')

    nC = 0
    if infile is not None:
        # 单一文件语料内容
        docs = getfilewords(infile)
        C = len(docs)
        n = 1
        for k,sp in enumerate(split):
            try:
                sp = int(sp)
            except:
                logging.info('%s is not number' %(sp,))
                continue
            if sp < 0 or sp >=100:
                continue
            else:
                file1 = genkeywordoutfile(infile, keywords='%d.%d' % (k, sp))
                file2 = genkeywordoutfile(infile, keywords='%d.%d' % (k, 100 - sp))
                # tc = C
                f1 = open(file1, mode='a+')
                f2 = open(file2, mode='a+')
                wf1 = copy.deepcopy(docs)
                wf2 = []
                wi = random.sample(range(0,C), int(C * sp / 100))
                for i in wi:
                    f1.write(' '.join([words for words in wf1[i][0]]) + '%s%s\n' % (label,txtType))
                    logging.info('%s == %d' %(file1,i))
                f1.close()
                for i in sorted(wi,reverse=True):
                    del wf1[i]

                for wf in wf1:
                    f2.write(' '.join([words for words in wf[0]]) + '%s%s\n' % (label,txtType))
                f2.close()
                logging.info('== == == == == == == == == == ==')
    else:
        print(usage)
