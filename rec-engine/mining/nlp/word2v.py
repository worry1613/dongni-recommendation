# -*- coding: utf-8 -*-
# @创建时间 : 19/2/2018
# @作者    : worry1613(549145583@qq.com)
# GitHub  : https://github.com/worry1613
# CSDN   : http://blog.csdn.net/worryabout/

from optparse import OptionParser
from gensim.models import word2vec
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# 使用gensim库中的word2vec类
class W2v(object):
    def __init__(self, fin=None):
        self.model = None
        self.file = fin

    def load(self, fmodel):
        self.model = word2vec.Word2Vec.load(fmodel)

    def process(self, size=300, window=5, min_count=5):
        import multiprocessing
        cpu_count = multiprocessing.cpu_count()
        workers = cpu_count
        sentences = word2vec.LineSentence(self.file)
        self.model = word2vec.Word2Vec(sentences, size=size, window=window, min_count=min_count, workers=workers)

    def save(self, fout):
        try:
            self.model.save(fout)
        except IOError:
            print(fout, "写文件取错误请检查!")
            exit(0)


if __name__ == '__main__':
    '''
    python word2v.py -f ../../../data/新闻min_cw.txt  -m ../../../model/w2v.300.新闻min.model
    '''
    parser = OptionParser()
    parser.add_option('-f', '--file', type=str, help='已经分了词的语料库文件', dest='wordsfile')
    parser.add_option('-m', '--model', type=str, help='训练完成了w2v模型文件', dest='modelfile')
    parser.add_option('-s', '--size', type=int, default=300, help='w2v向量维度')

    options, args = parser.parse_args()
    if not (options.wordsfile or options.modelfile):
        parser.print_help()
        exit()

    w = W2v(options.wordsfile)
    logging.info('<<<<<<<<<<<<<<<<')
    w.process()
    logging.info('>>>>>>>>>>>>>>>>')
    w.save(options.modelfile)
