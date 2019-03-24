#!/usr/bin/python
# -*- encoding:utf-8 -*-
# 作者:王睿
# 创建时间:2015.7.3
# 邮箱:
# GitHub: https://github.com/worry1613
# CSDN:
#
# 处理语料内容，把单一目录内所有文件的内容变成一个文件内的逐条的内容，并加上类别名
# dirtofile.py 语料内容目录
#
import sys,os
import traceback

reload(sys)
sys.setdefaultencoding('utf8')

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def getfilewords(f,type='line'):
    """
    操作语料文件
    :param f:     文件名
    :param type:  操作类型，line-文件每行一个语料，file-文件全部内容是一个语料
    :return:    type, words
    """
    doc = ''
    txtType = getType(f)
    file = open('%s/%s' % (sys.path[0], f))
    try:
        docs = file.read()
        doc = tran2UTF8(docs).replace("\n", "").replace("\r", "")
    except:
        pass
    finally:
        file.close()
    return doc

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
        fs = ps[-2]
        return fs

def getCoding(strInput):
    '''
    获取编码格式
    '''
    if isinstance(strInput, unicode):
        return "unicode"
    try:
        strInput.decode("utf8")
        return 'utf8'
    except:
        pass
    try:
        strInput.decode("gbk")
        return 'gbk'
    except:
        pass

def tran2UTF8(strInput):
    '''
    转化为utf8格式
    '''
    strCodingFmt = getCoding(strInput)
    if strCodingFmt == "utf8":
        return strInput
    elif strCodingFmt == "unicode":
        return strInput.encode("utf8")
    elif strCodingFmt == "gbk":
        return strInput.decode("gbk").encode("utf8")
    elif strCodingFmt == "gb2312":
        return strInput.decode("gb18030").encode("utf8")

def getTypeDir(dir,txtType='.'):
    """
    返回类型名
    :param file:      目录
    :return:          主目录名
    ./www/中文/       中文
    中文/             中文
    ../ww/中文名/     中文文件名

    """
    words = []
    word=''
    txtType = txtType
    ps = dir.strip('').split('/')
    dirs = os.listdir(dir)
    curdir = None
    curtype = None
    for file in dirs:
        curdir = '%s%s/' % (dir, file)
        if file == '.DS_Store':
            continue
        elif os.path.isdir(curdir):
            curtype = '%s-%s' % (txtType, file)
            # txtType = file
            t,w = getTypeDir(curdir,file)
            words.append((t,w))
        else:
            curdirfile = '%s/%s' % (dir, file)
            word+=getfilewords(curdirfile,type='file')
            word+='\r\n'
            logging.info('[%s] [%s] is ok' %(txtType,curdir,))
    if txtType == '.':

        for w in words:
            curfile = '%sclass-%s.txt'%(dir,w[0])
            typefile = open(curfile,mode='w')
            typefile.write(w[1])
            typefile.close()
            logging.info('%s is ok'%(curfile))
        if word != '':
            curfile = '%sclass-*.txt' % (dir, )
            typefile = open(curfile, mode='w')
            typefile.write(word)
            typefile.close()
            logging.info('%s is ok' % (curfile))

    return txtType,word

if __name__ == '__main__':
    usage = """
            处理语料内容，把单一目录内所有文件的内容变成一个文件内的逐条的内容，并加上类别名

            dirtofile.py 语料内容目录
            dirtofile.py ../中文语料库/SogouC.reduced/Reduced/
            """
    if len(sys.argv) == 1:
        print usage
        exit()
    curdir = sys.argv[1]
    getTypeDir(curdir)
