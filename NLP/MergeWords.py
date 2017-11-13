# #!/usr/bin/python
# -*- coding:utf-8 -*-
#
# 作者:王睿
# 创建时间:2015.7.3
# 邮箱:
# GitHub:
# CSDN:
#
# 主要用来合并字典文件，停词字典，关键词字典.....
# MergeWrods.py  -i 字典文件名 -o 合并后的文件
#
# ex:
# MergeWrods.py  -i s*.txt -o ~/stopword.txt
# 合并/stop目录下s1.txt和s2.txt，合并后的文件是~/stopword.txt
#
# MergeWrods.py /stop/*  -o ~/stopword.txt
# 合并/stop目录下的所有文件，合并后的文件是~/stopword.txt
#
import getopt
import glob
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# 获取词集的Set
def GetSetOfStopWords(filepath):
    f_stop = open(filepath)
    try:
        f_stop_text = f_stop.read()
        f_stop_text = unicode(f_stop_text, 'utf-8')
    finally:
        f_stop.close()
    f_stop_seg_list = f_stop_text.split('\n')

    return set(f_stop_seg_list)

# 保存Set
def SaveSet(set, filename):
    f_stop = open(filename, 'w')
    set = list(set)
    for item in range(len(set)):
        if item != len(set):
            f_stop.writelines((set[item].encode('utf-8')) + '\n')
        else:
            f_stop.writelines(set[item].encode('utf-8'))
    print '合并后%s, 共%d词' % (filename,len(set))
    f_stop.close()


# 求Set并集
def GetSetUnion(list):
    listOfSet = []
    for item in list:
        words = GetSetOfStopWords(item)
        listOfSet.append(words)
        print '%s,共%d词' % (item,len(words))
    SetUnion = set('!')
    for item in listOfSet:
        SetUnion = SetUnion | item

    return SetUnion

def GetStopWords(listOfFileName, FileName='words.txt'):
    SetUnion = GetSetUnion(listOfFileName)
    SaveSet(SetUnion, FileName)

if __name__ == '__main__':
    usage = """
    主要用来合并字典文件，停词字典，关键词字典.....
    MergeWrods.py -i 字典文件名1 -o 合并后的文件

    -i files        要合并的字典文件，支持通配符
    -o file         保存成文件，不写文件名用默认文件名，默认文件是words.txt


    MergeWrods.py  -i s*.txt -o ~/stopword.txt
    合并/stop目录下s*.txt的所有文件，合并后的文件是~/stopword.txt

    MergeWrods.py /stop/*  -o ~/stopword.txt
    合并/stop目录下的所有文件，合并后的文件是~/stopword.txt
    """

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["in=", "out="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()
    infile = 0
    outfile = 'words.txt'
    # dir = './'
    for k, v in opts:
        if k in ('-o', '--out'):
            outfile = v.strip()
        elif k in ('-i', '--in'):
            infile = v.strip()
        elif k in ('-h', '--help'):
            print(usage)
            exit()
    print('in=%s,out=%s' % (infile, outfile))
    if infile is not 0:
        files = [f for f in glob.glob(infile)]
        GetStopWords(files,outfile)
    else:
        print(usage)