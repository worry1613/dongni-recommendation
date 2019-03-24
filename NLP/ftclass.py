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

from simhash import Simhash

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
    s1 = """我们知道，在文本去重的时候，有很多方式，在文本与文本之间对比，如果是整篇对比，费时费力，有人就想到用什么东西代表每篇文章，如摘要，当然，对计算机来说，摘要和整篇的区别只是缩小了篇幅，所以又有人想到了采用关键字来对比。这样确实可以大大缩减我们对比的复杂性。那我们怎么得到一篇文章的关键字呢？一般采用词频（TF），但是只用词频，如中文出现类似“的”、“我们”之类的词语很多，应该怎么去掉这些词语呢，手动去掉实在是麻烦，于是可以结合逆向词频（IDF)，这就是著名的TD-IDF，一种提取一个文章的关键词的算法。词频我们很好理解，一个词语在整篇文章中出现的次数与词语总个数之比。IDF又怎么算呢，假如一个词语，在我们所有文章中出现的频率都非常高（例如“的”在我们多个文本中出现的次数很多），我们就认为，这个词语不具有代表性，就可以降低其作用，也就是赋予其较小的权值。
    那这个权重，我们怎么计算呢，（这里敲公式比较麻烦，直接找来图片），如下图，分子代表文章总数，分母表示该词语在这些文章（|D|）出现的篇数。一般我们还会采取分母加一的方法，防止分母为0的情况出现，在这个比值之后取对数，就是IDF了。
    simhash是一种局部敏感hash。我们都知道什么是hash。那什么叫局部敏感呢，假定A、B具有一定的相似性，在hash之后，仍然能保持这种相似性，就称之为局部敏感hash。
    在上文中，我们得到一个文档的关键词，取得一篇文章关键词集合，又会降低对比效率，我们可以通过hash的方法，把上述得到的关键词集合hash成一串二进制，这样我们直接对比二进制数，看其相似性就可以得到两篇文档的相似性，在查看相似性的时候我们采用海明距离，即在对比二进制的时候，我们看其有多少位不同，就称海明距离为多少。在这里，我是将文章simhash得到一串64位的二进制，一般取海明距离为3作为阈值，即在64位二进制中，只有三位不同，我们就认为两个文档是相似的。当然了，这里可以根据自己的需求来设置阈值。
    就这样，我们把一篇文档用一个二进制代表了，也就是把一个文档hash之后得到一串二进制数的算法，称这个hash为simhash。
    具体simhash步骤如下：
    （1）将文档分词，取一个文章的TF-IDF权重最高的前20个词（feature）和权重（weight）。即一篇文档得到一个长度为20的（feature：weight）的集合。
    （2）对其中的词（feature），进行普通的哈希之后得到一个64为的二进制，得到长度为20的（hash : weight）的集合。
    （3）根据（2）中得到一串二进制数（hash）中相应位置是1是0，对相应位置取正值weight和负值weight。例如一个词进过（2）得到（010111：5）进过步骤（3）之后可以得到列表[-5,5,-5,5,5,5]，即对一个文档，我们可以得到20个长度为64的列表[weight，-weight...weight]。
    （4）对（3）中20个列表进行列向累加得到一个列表。如[-5,5,-5,5,5,5]、[-3,-3,-3,3,-3,3]、[1,-1,-1,1,1,1]进行列向累加得到[-7，1，-9，9，3，9]，这样，我们对一个文档得到，一个长度为64的列表。
    （5）对（4）中得到的列表中每个值进行判断，当为负值的时候去0，正值取1。例如，[-7，1，-9，9，3，9]得到010111，这样，我们就得到一个文档的simhash值了。
    （6）计算相似性。连个simhash取异或，看其中1的个数是否超过3。超过3则判定为不相似，小于等于3则判定为相似。
    呼呼呼，终于写完大致的步骤，可参考下图理解步骤。"""
    s2 = """我们知道，在文本去重的时候，有很多方式，在文本与文本之间对比，如果是整篇对比，费时费力，有人就想到用什么东西代表每篇文章，如摘要，当然，对计算机来说，摘要和整篇的区别只是缩小了篇幅，所以又有人想到了采用关键字来对比。这样确实可以大大缩减我们对比的复杂性。那我们怎么得到一篇文章的关键字呢？一般采用词频（TF），但是只用词频，如中文出现类似“的”、“我们”之类的词语很多，应该怎么去掉这些词语呢，手动去掉实在是麻烦，于是可以结合逆向词频（IDF)，这就是著名的TD-IDF，一种提取一个文章的关键词的算法。词频我们很好理解，一个词语在整篇文章中出现的次数与词语总个数之比。IDF又怎么算呢，假如一个词语，在我们所有文章中出现的频率都非常高（例如“的”在我们多个文本中出现的次数很多），我们就认为，这个词语不具有代表性，就可以降低其作用，也就是赋予其较小的权值。
    那这个权重，我们怎么计算呢，（这里敲公式比较麻烦，直接找来图片），如下图，分子代表文章总数，分母表示该词语在这些文章（|D|）出现的篇数。一般我们还会采取分母加一的方法，防止分母为0的情况出现，在这个比值之后取对数，就是IDF了。
    simhash是一种局部敏感hash。我们都知道什么是hash。那什么叫局部敏感呢，假定A、B具有一定的相似性，在hash之后，仍然能保持这种相似性，就称之为局部敏感hash。
    在上文中，我们得到一个文档的关键词，取得一篇文章关键词集合，又会降低对比效率，我们可以通过hash的方法，把上述得到的关键词集合hash成一串二进制，这样我们直接对比二进制数，看其相似性就可以得到两篇文档的相似性，在查看相似性的时候我们采用海明距离，即在对比二进制的时候，我们看其有多少位不同，就称海明距离为多少。在这里，我是将文章simhash得到一串64位的二进制，一般取海明距离为3作为阈值，即在64位二进制中，只有三位不同，我们就认为两个文档是相似的。当然了，这里可以根据自己的需求来设置阈值。
    就这样，我们把一篇文档用一个二进制代表了，也就是把一个文档hash之后得到一串二进制数的算法，称这个hash为simhash。
    具体simhash步骤如下：
    （1）将文档分词，取一个文章的TF-IDF权重最高的前20个词（feature）和权重（weight）。即一篇文档得到一个长度为20的（feature：weight）的集合。
    （2）对其中的词（feature），进行普通的哈希之后得到一个64为的二进制，得到长度为20的（hash : weight）的集合。
    （3）根据（2）中得到一串二进制数（hash）中相应位置是1是0，对相应位置取正值weight和负值weight。例如一个词进过（2）得到（010111：5）进过步骤（3）之后可以得到列表[-5,5,-5,5,5,5]，即对一个文档，我们可以得到20个长度为64的列表[weight，-weight...weight]。
    """
import lshash
    # a1 = Simhash('How are you? I AM fine. Thanks. And you?')
    # a2 = Simhash('How old are you ? :-) i am fine. Thanks. And you?')
    a1 = Simhash(s1)
    a2 = Simhash(s2)
    ret = a1.distance(a2)
    print(ret)
    exit(0)




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
