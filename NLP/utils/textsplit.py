# -*- encoding:utf-8 -*-
# 作者:王睿
# 创建时间:2015.7.3
# 邮箱:
# GitHub: https://github.com/worry1613
# CSDN:
#
# 切分训练和测试数据集
# textsplit.py -i 语料文件名  -n 切分比例
#
#        -i file         单一语料库文件，文件名默认为类型名，文件内每行默认为一个输入内容
#        -n split        切分比例，多个用逗号分开,
#
#        textsplit.py  -i s.txt  -n 15
#        textsplit.py  -i ss.txt -n 15,25,30
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
        textsplit.py -i 语料文件名 -n 切分比例

        -i file         单一语料库文件，文件名默认为类型名，文件内每行默认为一个输入内容
        -n split        切分比例，多个用逗号分开
        
        textsplit.py  -i s.txt  -n 15
        textsplit.py  -i ss.txt -n 15,25,30
        """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:n:", ["input=", "split="])
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
        elif k in ('-h', '--help'):
            print(usage)
    nC = 0
    if infile is not None:
        # 单一文件语料内容
        docs = open(infile).read().splitlines()
        C = len(docs)

        for k,sp in enumerate(split):
            n = 0
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
                for line in docs:
                    if n in wi:
                        f1.write(line+'\n')
                    else:
                        f2.write(line+'\n')
                    n+=1
                    logging.info('%d--' % (n,))
                f1.close()
                f2.close()
                logging.info('== == == == == == == == == == ==')
    else:
        print(usage)
