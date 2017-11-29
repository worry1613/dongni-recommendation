# -*- encoding:utf-8 -*-
"""
作者:王睿
创建时间:2017.5.3
邮箱:
GitHub: https://github.com/worry1613
CSDN:


    ftclass.py -r 训练数据集文件名 -t 测试数据集文件名 -m 模型文件名

    -r file        训练数据集文件名
    -t file        测试数据集文件名
    -m file        模型文件名
    -l label       关键词和类别之间的分隔符，"__label__"

    ftclass.py  -r train.txt  -t test.txt -m model.bin -c a,b,c,d,e  -l __|||__

"""
import getopt
import json

import fasttext

import jieba
import os,sys

from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf8')
import logging
import fasttext

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

##生成fastext的训练和测试数据集
ftrain = None
ftest = None
fmodel = None
tyes = None
label = "__label__"


_get_abs_path = lambda path: os.path.normpath(os.path.join(os.getcwd(), path))


def fasttext_sample(tr,te,mo,label):
    strain = datetime.now()
    classifier = fasttext.supervised(tr, mo, label_prefix=label)
    stest = datetime.now()
    result = classifier.test(te)
    etest = datetime.now()
    print '训练开始时间:%s,结束时间:%s, 共耗时%d秒' % (strain,stest,(stest-strain).seconds)
    print '测试开始时间:%s,结束时间:%s, 共耗时%d秒' % (stest,etest,(etest-stest).seconds)
    print '准确率:%f,如回率:%f' % (result.precision,result.recall)
    return classifier

def fasttext_classanalyze(mo,te):
    classifier = fasttext.load_model(mo)
    labels_right = []
    texts = []
    with open(te) as fr:
        lines = fr.readlines()
    for line in lines:
        labels_right.append(line.split("__label__")[1].rstrip())
        texts.append(line.split("__label__")[0])
    labels_predict = [str(e[0].split('__label__')[1]) for e in classifier.predict(texts)]  # 预测输出结果为二维形式

    text_labels = list(set(labels_right))
    text_predict_labels = list(set(labels_predict))
    # print(text_predict_labels)
    # print(text_labels)
    A = dict.fromkeys(text_labels, 0)  # 预测正确的各个类的数目
    B = dict.fromkeys(text_labels, 0)  # 测试数据集中各个类的数目
    C = dict.fromkeys(text_predict_labels, 0)  # 预测结果中各个类的数目
    for i in range(0, len(labels_right)):
        B[labels_right[i]] += 1
        C[labels_predict[i]] += 1
        if labels_right[i] == labels_predict[i]:
            A[labels_right[i]] += 1
    print(json.dumps(A, indent=4,ensure_ascii=False))
    print(json.dumps(B, indent=4,ensure_ascii=False))
    print(json.dumps(C, indent=4,ensure_ascii=False))
    # 计算准确率，召回率，F值
    for key in B:
        p = float(A[key]) / float(B[key])
        if C.has_key(key):
            r = float(A[key]) / float(C[key])
        else:
            r=0
        if (p + r) >0:
            f = p * r * 2 / (p + r)
        else:
            f = 0
        print ("%s:\tp:%f\tr:%f\tf:%f" % (key, p, r, f))
        # print labels_predict
    text_labels = list(set(labels_right))
    text_predict_labels = list(set(labels_predict))
    print(json.dumps(text_predict_labels, indent=4,ensure_ascii=False) )
    print(json.dumps(text_labels, indent=4,ensure_ascii=False))


if __name__ == '__main__':
    usage = """  
            ftclass.py -r 训练数据集文件名 -t 测试数据集文件名 -m 模型文件名

            -r file        训练数据集文件名
            -t file        测试数据集文件名
            -m file        模型文件名
            -l label       关键词和类别之间的分隔符，"__label__"

            ftclass.py  -r train.txt  -t test.txt -m model.bin -c a,b,c,d,e  -l __|||__
            """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "r:t:m:c:l", ["train=", "test=", "model=", "class=", "label="])
    except getopt.GetoptError:
        # print help information and exit:
        print(usage)
        exit()
    if len(opts) == 0:
        print(usage)
        exit()
    for k, v in opts:
        if k in ('-r', '--train'):
            if v != '':
                ftrain = v
        elif k in ('-t', '--test'):
            ftest = v
        elif k in ('-m', '--model'):
            fmodel = v
        elif k in ('-c', '--class'):
            types = v.split(',')
        elif k in ('-l', '--label'):
            label = v
        elif k in ('-h', '--help'):
            print(usage)
    nC = 0
    if ftrain is not None and ftest is not None and fmodel is not None:
        # 单一文件语料内容
        modelclass = fasttext_sample(tr=ftrain,te=ftest,mo=fmodel,label=label)
        fasttext_classanalyze(mo=fmodel+'.bin',te=ftest)
    else:
        print(usage)
