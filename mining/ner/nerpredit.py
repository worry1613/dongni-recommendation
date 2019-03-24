# -*- coding: utf-8 -*-
# @创建时间 : 15/3/2019 
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# @CSDN   : http://blog.csdn.net/worryabout/
import getopt

import sys

import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def load_model(path):
    import os, CRFPP
    # -v 3: access deep information like alpha,beta,prob
    # -nN: enable nbest output. N should be >= 2
    if os.path.exists(path):
        return CRFPP.Tagger('-m {0} -v 3 -n2'.format(path))
    raise RuntimeError('模形文件 %s 不存在！'% (path,))

def NER_bmewo(tagger,text):

    for c in text:
        if c :
            tagger.add(c)

    result = []

    # parse and change internal stated as 'parsed'
    tagger.parse()
    word = ''
    for i in range(0, tagger.size()):
        for j in range(0, tagger.xsize()):
            ch = tagger.x(i, j)
            tag = tagger.y2(i)
            if tag[0] == 'B':
                word = ch
            elif tag[0] == 'M':
                word += ch
            elif tag[0] == 'E':
                word += ch
                result.append(word)
                word = ''
            elif tag[0] == 'O':
                # word = ch
                # result.append(word)
                pass
    tagger.clear()
    return result

def NER_bio(tagger,text):

    for c in text:
        if c :
            tagger.add(c)

    result = []

    # parse and change internal stated as 'parsed'
    tagger.parse()
    word = ''
    for i in range(0, tagger.size()):
        for j in range(0, tagger.xsize()):
            ch = tagger.x(i, j)
            tag = tagger.y2(i)
            if tag[0] == 'B':
                if not word:
                    word = ch
                else:
                    result.append(word)
            elif tag[0] == 'I':
                word += ch
            elif tag[0] == 'O':
                if word:
                    result.append(word)
                    word = ''
    return result


if __name__ == '__main__':
    usage = """  
                    nerpredit.py -l model文件 -t 预测文本内容 -f 预测文件

                    -l file        model文件
                    -t txt         需要用ner分析的单行文本，与-f互斥，优先级高
                    -f file        需要用ner分析的文本文件，一行或多行
                    -d dataformat  标注格式, bio,bmewo,默认bio

                    nerpredit.py  -l model/model_bio_pos -t  5月09日消息快评深度报告权威内参来自“证券通”www.KL178.com今日热点：五一长假过后，人民币再度逼近8元关口，中间价达8.0090。证券通认为，由于市场预期美联储将在今年6月暂停升息，导致了国际市场上美元走势疲软，从而推高了人民币汇率。各方均预计人民币长期持续升值将不可避免，突破8元几成定局，摩根斯坦利甚至认为年底前人民币将升值至7.5元。基于此种态势，预期未来市场中房地产板块可能仍将在人民币升值影响下稳步上扬，而对外贸依赖度较高的企业则有可能面临业绩下滑的危险。但就近期来说，8元关口作为一个重要的心理位可能仍有反复，投资者不应过于乐观。更多详情免费咨询021*64690729或登录WWW.KL178.COM（证券通），资深行业研究员为您提供客观、深度、超前的投资信息。作者声明：在本机构、本人所知情的范围内,本机构、本人以及财产上的利害关系人与所述文章内容没有利害关系。本版文章纯属个人观点,仅供参考,文责自负。读者据此入市,风险自担。 
                    nerpredit.py  -l model/model_bio_pos -f  data/nerpredit.txt  
                    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "l:t:f:d:h", ["load=", "txt=", "file=", "dataformat=", "help="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()

    fmodel = None
    fptxt = None
    fpfile = None
    dmap = {'bio':NER_bio,'bmewo':NER_bmewo}
    df = 'bio'
    for k, v in opts:
        if k in ('-t', '--txt'):
            if v != '':
                fptxt = v
        elif k in ('-l', '--load'):
            fmodel = v
        elif k in ('-f', '--file'):
            fpfile = v
        elif k in ('-d', '--dataformat'):
            df = v
        elif k in ('-h', '--help'):
            print(usage)
            exit()
    if not fpfile and not fptxt:
        print(usage)
        exit()
    tagger = load_model(fmodel)
    if fptxt:
        print(dmap.get(df)(tagger, fptxt))
    else:
        f = open(fpfile)
        lines = f.readlines()
        f.close()
        for text in lines:
            print(dmap.get(df)(tagger, text))